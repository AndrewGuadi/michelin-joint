from flask import Flask, render_template, request, session, redirect, url_for, flash
from forms import LoginForm, CreateAccount, DiscoverForm
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from extensions import db
from sqlalchemy.exc import IntegrityError
from helpers import read_json, check_stars
from location_helpers import haversine, get_coordinates
import os

app = Flask(__name__)

#database info
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reconegut.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#import the tables
from models import User, Restaurant, CheckIn, Friendship

app.config['SECRET_KEY'] = "TEST_KEY_NEEDS_CHANGED"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



#user_loader
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():

    login_form = LoginForm()
    if login_form.validate_on_submit():
        #add all the user creation and validation
        user = User.query.filter_by(username = login_form.username.data.strip()).first()
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



@app.route('/register', methods=['GET', 'POST'])
def register():
    create_form = CreateAccount()
    if create_form.validate_on_submit():
        # Check if the username or email already exists
        existing_user = User.query.filter(
            (User.username == create_form.username.data.strip()) |
            (User.email == create_form.email.data.strip())
        ).first()

        if existing_user:
            flash('Username or Email already exists', 'error')
            return render_template('register.html', create_account_form=create_form)

        user = User(username=create_form.username.data, email=create_form.email.data)
        user.set_password(create_form.password.data)
        
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
    if not checkins:
        # Handle case where there are no check-ins for the user
        flash("No check-ins available for this user.", "info")
    return render_template('index.html', checkins=checkins, user=current_user, active_page='home')


@app.route('/discover', methods=['GET'])
@login_required
def discover():
    form = DiscoverForm()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    paginated_restaurants = Restaurant.query.paginate(page=page, per_page=per_page, error_out=False)

    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('restaurant_partial.html', restaurants=paginated_restaurants.items)
    return render_template('discover2.html', active_page='discover', restaurants=paginated_restaurants.items, pagination=paginated_restaurants, form=form)


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
    filtered_restaurants = [res for res in filtered_restaurants if res.longitude is not None and res.latitude is not None]
    for resta in filtered_restaurants:
        print(resta.name)
    # Check if location filter is applied and sort by distance
    if location:
        print(location)
        # Convert user_location string to coordinates here if needed
        user_location = get_coordinates(location)  # Example coordinates, replace with actual user location
        filtered_restaurants = sorted(filtered_restaurants, key=lambda res: haversine(user_location[1], user_location[0], res.longitude, res.latitude))
    
    # Manual pagination after sorting
    start = (page - 1) * per_page
    end = start + per_page
    paginated_restaurants = filtered_restaurants[start:end]

    return render_template('discover2.html', 
                           restaurants=paginated_restaurants, 
                           pagination=None,  # Handle pagination in template if necessary
                           form=form)




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
    return render_template('restaurants.html', res=restaurant, checkins=checkins)



@app.route('/checkin/<restaurant>', methods=['POST'])
@login_required
def checkin(restaurant):
    if request.method == "POST":
        user_id = current_user.id
        restaurant = Restaurant.query.filter_by(name=restaurant).first()
        restaurant_id = restaurant.id
        checkin = CheckIn(user_id=user_id, restaurant_id=restaurant_id)        
        current_user.total_stars += check_stars(restaurant.distinction)
        
        try:
            db.session.add(checkin)
            db.session.commit()
            flash('Successfully checked in at ' + restaurant.name, 'success')
        except:
            db.session.rollback()
        
    return redirect(url_for('restaurants', restaurant_name=restaurant.name))


if __name__ == '__main__':
    app.run(debug=True)
