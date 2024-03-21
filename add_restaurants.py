
from app import db, User, Restaurant, CheckIn, Friendship, app
from helpers import read_json
import time




if __name__=="__main__":
    #read into memory the json item
    restaurants = read_json('static/data/michelin-guide.json')
    with app.app_context():
        
        for res in restaurants:
            r1 = Restaurant()
            r1.phone = res.get('phone')            
            r1.name = res.get('name')            
            r1.distinction = int(res.get('distinction')[0])            
            r1.style = res.get('style')            
            r1.res_url = res.get('url')            
            r1.description = res.get('description')            
            r1.location = res.get('address')            
            r1.image_url = res.get('image_url')
            r1.latitude = res.get('latitude')
            r1.longitude = res.get('longitude')
            if "https://www.guide.michelin.com/us/en/hotels-stays" in res.get('michelin_url'):
                print('Exiting Loop')
                continue       
            r1.michelin_url = res.get('michelin_url')
            db.session.add(r1)
            print(f'{r1} added to session')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"There was an error: {e}")
            time.sleep(4)