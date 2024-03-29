

from app import app, Content, Chef, db
from helpers import read_json

with app.app_context():

    content = read_json('static/data/content.json')
    for item in content:
        #get the proper chef:
        found_chef = Chef.query.filter_by(name=item.get('chef')).first()
        if found_chef:
            new_content = Content(title=item.get('title'),
                                content_type=item.get('content_type'),
                                url=item.get('link'),
                                image_url=item.get('image'),
                                associated_id=found_chef.id,
                                associated_type='chef')
            
            try:
                db.session.add(new_content)
                db.session.commit()
                print("Successfully added data to content table")
            except:
                db.session.roll_back()

