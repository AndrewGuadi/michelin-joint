from app import app, db
import os


if os.path.exists('instance/reconegut.db'):
    print('Deleting Old Database')
    os.remove('instance/reconegut.db')


with app.app_context():
    db.create_all()

