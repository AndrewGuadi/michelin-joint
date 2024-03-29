

from app import db, app, Chef
from helpers import read_json
import json


with app.app_context():
    chefs = read_json('static/data/chefs-data.json')
    details = read_json('static/data/all_chefs_details.json')
    
    for chef in chefs:
        name = chef.get('chef')
        db_chef = Chef.query.filter_by(name=name).first()
        if details.get(name):
            detail = json.dumps(details[name])
            db_chef.details = detail
            try:
                db.session.add(db_chef)
                db.session.commit()
                print(f"Added details to {name}")
            except:
                db.session.rollback()
            ##add detail to the details column of the flask database



