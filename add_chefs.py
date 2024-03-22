from extensions import db
from helpers import read_json
from app import Chef, app, Restaurant

if __name__ == "__main__":
    # Read into memory the json item
    restaurants = read_json('static/data/michelin-guide.json')
    chefs = read_json('static/data/chefs-data.json')
    
    with app.app_context():
        for chef_data in chefs:
            if chef_data.get('chef'):
                new_chef = Chef(name=chef_data.get('chef'), bio=chef_data.get('blurb'))
                db.session.add(new_chef)  # Add new_chef to the session here
                print(new_chef)
                for restaurant_name in chef_data.get('current_restaurant', []):
                    restaurant = Restaurant.query.filter_by(name=restaurant_name).first()
                    if restaurant:
                        new_chef.restaurants.append(restaurant)
                
                db.session.commit()  # Commit after all modifications are done
            else:
                # Handle the case where 'chef' key is missing or the value is None
                print('Failed')

            # Handle exceptions if any
            try:
                db.session.commit()
            except Exception as e:
                print('Failed to upload data:', e)
                db.session.rollback()

    print('Complete')