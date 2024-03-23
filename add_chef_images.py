
from helpers import read_json
from app import app, Chef, db

chefs = read_json('static/data/chefs-data.json')

with app.app_context():

    for index, chef in enumerate(chefs):
        d_chef = Chef.query.filter_by(name=chef.get('chef')).first()
        if d_chef:
            d_chef.profile_picture = chef.get('image_url')

            try:
                db.session.add(d_chef)
                db.session.commit()

            except Exception as e:
                print(f'Unable to Commit:  {e}')
                db.session.rollback()
    
    print('Successfully Uploaded images to every chef')

