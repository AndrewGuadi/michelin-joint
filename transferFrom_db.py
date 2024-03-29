
from app import app, User, Follow
import json



def serialize(model_instance):
    """ Serialize a SQLAlchemy model instance. """
    return {column.name: getattr(model_instance, column.name) 
            for column in model_instance.__table__.columns}

with app.app_context():

    
    users = User.query.all()
    serialized_data = [serialize(user) for user in users]


    with open('user_db.json', 'w') as file:
        json.dump(serialized_data, file)

    users = User.query.all()
    serialized_data = [serialize(user) for user in users]


    with open('user_db.json', 'w') as file:
        json.dump(serialized_data, file)

    users = User.query.all()
    serialized_data = [serialize(user) for user in users]


    with open('user_db.json', 'w') as file:
        json.dump(serialized_data, file)