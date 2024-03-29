
from helpers import read_json
from app import app, User, db


users_data = read_json('user_db.json')

with app.app_context():

    for user_data in users_data:
        user = User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            total_stars=user_data.get('total_stars', 0),  # Using .get to handle cases where it might be missing
            _password_hash=user_data['_password_hash']
        )
        try:
            db.session.add(user)
            db.session.commit()

        except:
            db.session.rollback()