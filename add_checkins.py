
from app import db, User, Restaurant, CheckIn, Friendship, app




if __name__=="__main__":
    
    with app.app_context():

        user = User.query.filter_by(username='username').first()
        
        check_1 = CheckIn(user_id = user.id, restaurant_id=5, comment="Amazing Place to eat")
        check_2 = CheckIn(user_id = user.id, restaurant_id=324)
        check_3 = CheckIn(user_id = user.id, restaurant_id=1234, comment='First Michelin Star!')
        
        db.session.add(check_1)
        db.session.add(check_2)
        db.session.add(check_3)

        try:
            db.session.commit()
            print("Checkins Successfully Added")

        except Exception as e:
            print(f'There was an error: {e}')
            db.session.rollback()