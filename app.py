from flask import Flask, render_template, request, session, redirect, url_for, flash, make_response
from forms import LoginForm, CreateAccount, DiscoverForm
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from extensions import db
from sqlalchemy.exc import IntegrityError
from helpers import read_json, check_stars
from location_helpers import haversine, get_coordinates
import os
import json

app = Flask(__name__)

#database info
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reconegut.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#import the tables
from models import User, Restaurant, CheckIn, Friendship, Chef, Follow

app.config['SECRET_KEY'] = "TEST_KEY_NEEDS_CHANGED"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



#user_loader
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def get_followed_entities(user_id):
    followed_entities = Follow.query.filter_by(follower_id=user_id).all()
    
    followed_chefs = []
    followed_restaurants = []

    for entity in followed_entities:
        if entity.followed_type == 'chef':
            chef = Chef.query.get(entity.followed_id)
            if chef:
                followed_chefs.append(chef)
        elif entity.followed_type == 'restaurant':
            restaurant = Restaurant.query.get(entity.followed_id)
            if restaurant:
                followed_restaurants.append(restaurant)

    return followed_chefs, followed_restaurants


@app.route('/login', methods=['GET', 'POST'])
def login():

    login_form = LoginForm()
    if login_form.validate_on_submit():
        #add all the user creation and validation
        user = User.query.filter_by(username = login_form.username.data.lower().strip()).first()
        print(login_form.password.data)
        if user and user.check_password(login_form.password.data.strip()):
            print('Found')
            login_user(user)
            current_user = user
            return redirect(url_for('home'))
        else:
            print('Not Found')
            flash("Username/Password were not found", 'error')
    return render_template('login.html', login_form=login_form)


@app.route('/privacy-policy')
def privacy_policy():

    with open('static/data/privacy-policy.txt', 'r', encoding='utf-8') as file:
        privacy = file.read()

    return render_template('privacy-policy.html', privacy=privacy)



@app.route('/register', methods=['GET', 'POST'])
def register():
    create_form = CreateAccount()
    if create_form.validate_on_submit():
        # Check if the username or email already exists
        existing_user = User.query.filter(
            (User.username == create_form.username.data.lower().strip()) |
            (User.email == create_form.email.data.lower().strip())
        ).first()

        if existing_user:
            flash('Username or Email already exists', 'error')
            return render_template('register.html', create_account_form=create_form)

        user = User(username=create_form.username.data.lower().strip(), email=create_form.email.data.lower().strip())
        user.set_password(create_form.password.data.strip())
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account successfully created', 'success')
            return redirect(url_for('login'))

        except IntegrityError:
            db.session.rollback()
            flash('Username or Email already exists', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Registration error: ' + str(e), 'error')
    else:
        for field, errors in create_form.errors.items():
            for error in errors:
                app.logger.warning(f"Error in the {field} field - {error}")
                flash(f"Error in the {field} field - {error}", 'error')

    return render_template('register.html', create_account_form=create_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@app.route('/home')
@login_required
def home():
    # Assuming you're using Flask-Login and want to get check-ins for the current logged-in user
    user_id = current_user.id
    
    # Query to get all check-ins for the specific user along with associated restaurant data
    checkins = CheckIn.query.filter_by(user_id=user_id).all()
    chefs, restaurants = get_followed_entities(user_id=user_id)
    if not checkins:
        # Handle case where there are no check-ins for the user
        flash("No check-ins available for this user.", "info")
    return render_template('user-profile.html', checkins=checkins, user=current_user, chefs=chefs, active_page='home')


@app.route('/discover', methods=['GET'])
@login_required
def discover():
    form = DiscoverForm(request.args)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Base query for Restaurant
    query_conditions = Restaurant.query

    # Additional query conditions can be added here if needed

    # Fetch the paginated restaurants list
    paginated_restaurants = query_conditions.paginate(page=page, per_page=per_page, error_out=False)

    # Check if it's an AJAX request for infinite scroll
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('restaurant_partial.html', restaurants=paginated_restaurants.items)

    # For regular page requests
    return render_template('discover2.html', 
                           restaurants=paginated_restaurants.items,
                           total_pages=paginated_restaurants.pages, 
                           current_page=page,
                           form=form, active_page='discover')


@app.route('/search_results', methods=['GET'])
@login_required
def search_results():
    form = DiscoverForm(request.args)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    print([item.data for item in form])
    query = form.query.data.strip()
    location = None
    if form.location.data:
        location = form.location.data.strip()  # Assuming this is the user's location input
    style = form.style.data
    star_count = form.star_count.data

    # Base query
    query_conditions = Restaurant.query

    # Add conditions only if they are provided
    if query:
        query_conditions = query_conditions.filter(Restaurant.name.ilike(f'%{query}%'))
    if style:
        query_conditions = query_conditions.filter(Restaurant.style == style)
    if star_count:
        query_conditions = query_conditions.filter(Restaurant.distinction.ilike(f'%{star_count}%'))

    # Fetch the filtered restaurants list before sorting by location
    filtered_restaurants = query_conditions.all()
    # Sort by location if necessary
    if location:
        filtered_restaurants = [res for res in filtered_restaurants if res.longitude is not None and res.latitude is not None]
        user_location = get_coordinates(location)
        filtered_restaurants = sorted(filtered_restaurants, key=lambda res: haversine(user_location[1], user_location[0], res.longitude, res.latitude))
    
    total_restaurants = len(filtered_restaurants)
    total_pages = (total_restaurants + per_page - 1) // per_page

    # Manual pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_restaurants = filtered_restaurants[start:end]

    #reset the form
    form = DiscoverForm()
    print(len(paginated_restaurants), total_pages, page)
    return render_template('discover2.html', 
                           restaurants=paginated_restaurants, 
                           total_pages=total_pages,  # Added to handle pagination in the template
                           current_page=page,
                           form=form, active_page='discover')




@app.route('/top')
@login_required
def top():
    tops = read_json('static/data/topFifty.json')
    return render_template('top.html', restaurants=tops, active_page='top')


@app.route('/top-restaurants/<restaurant>')
@login_required
def top_restaurants(restaurant):
    print(restaurant)
    restaurants = read_json('static/data/topFifty.json')
    print(restaurants)
    top_res = [res for res in restaurants if res['name'] == restaurant][0]
    print(top_res)
    return render_template('top-restaurants.html', res=top_res, active_page='top')



@app.route('/restaurants/<restaurant_name>')
@login_required
def restaurants(restaurant_name):
    
    user_id = current_user.id
    restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
    checkins = CheckIn.query.filter_by(restaurant_id=restaurant.id).all()
    if not restaurant:
        # Handle case where restaurant is not found
        return render_template('error.html', message="Restaurant not found"), 404
    
    # Check if current user is following the chef
    is_following = Follow.query.filter_by(
        follower_id=current_user.id,
        followed_id=restaurant.id,
        followed_type='restaurant'
    ).first() is not None
    return render_template('restaurants.html', res=restaurant, checkins=checkins, is_following=is_following)


@app.route('/chef-profile/<chef>')
@login_required
def chefProfile(chef):

    chef = Chef.query.filter_by(name=chef).first()
    details = json.loads(chef.details)

    # Check if current user is following the chef
    is_following = Follow.query.filter_by(
        follower_id=current_user.id,
        followed_id=chef.id,
        followed_type='chef'
    ).first() is not None
    return render_template('chef-profile.html', chef=chef, details=details, is_following=is_following)


@app.route('/checkin/<restaurant>', methods=['POST'])
@login_required
def checkin(restaurant):
    if request.method == "POST":
        user_id = current_user.id
        restaurant = Restaurant.query.filter_by(name=restaurant).first()
        restaurant_id = restaurant.id
        checkin = CheckIn(user_id=user_id, restaurant_id=restaurant_id)        
        current_user.total_stars += restaurant.distinction
        
        try:
            db.session.add(checkin)
            db.session.commit()
            flash('Successfully checked in at ' + restaurant.name, 'success')
        except:
            db.session.rollback()
        
    return redirect(url_for('restaurants', restaurant_name=restaurant.name))



@app.route('/follow_unfollow/<int:entity_id>/<entity_type>', methods=['POST'])
@login_required
def follow_unfollow(entity_id, entity_type):
    user_id = current_user.id  # ID of the user
    existing_follow = Follow.query.filter_by(
        follower_id=user_id, 
        followed_id=entity_id, 
        followed_type=entity_type
    ).first()

    if existing_follow:
        # Unfollow
        db.session.delete(existing_follow)
        db.session.commit()
        flash(f'You have unfollowed this {entity_type}', 'info')
    else:
        # Follow
        new_follow = Follow(follower_id=user_id, followed_id=entity_id, followed_type=entity_type)
        db.session.add(new_follow)
        db.session.commit()
        flash(f'You are now following this {entity_type}', 'success')

    # Redirect back to the referring page
    return redirect(request.referrer or url_for('home'))






#########################################
# def get_user_related_content(user_id):
#     # Get followed entities
#     followed_chefs, followed_restaurants = get_followed_entities(user_id)

#     related_content = []

#     # Get content related to followed chefs
#     for chef in followed_chefs:
#         chef_content = Content.query.filter_by(associated_id=chef.id, associated_type='chef').all()
#         related_content.extend(chef_content)

#     # Get content related to followed restaurants
#     for restaurant in followed_restaurants:
#         restaurant_content = Content.query.filter_by(associated_id=restaurant.id, associated_type='restaurant').all()
#         related_content.extend(restaurant_content)

#     return related_content

if __name__ == '__main__':
    app.run(debug=True)
