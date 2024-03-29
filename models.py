
from extensions import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    total_stars = db.Column(db.Integer(), default=0, unique = False, nullable=True)
    check_ins = db.relationship('CheckIn', backref='user', lazy=True)
    _password_hash = db.Column(db.String(128), nullable=False)  # Rename to _password_hash for privacy

    def set_password(self, password):
        """Hashes the password and stores its hash."""
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self._password_hash, password)

    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Prevent password from being set directly."""
        raise AttributeError('password is not a direct settable attribute, use set_password method')

    def __repr__(self):
        return f'<User {self.username}>'

# Friendship association table
class Friendship(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# CheckIn model
class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    comment = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<CheckIn {self.id}>'



chef_restaurant_association = db.Table('chef_restaurant',
    db.Column('chef_id', db.Integer, db.ForeignKey('chef.id'), primary_key=True),
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurant.id'), primary_key=True)
)



class Chef(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text) 

    # Many-to-many relationship with restaurants
     # Define the relationship with Restaurant
    restaurants = db.relationship(
        'Restaurant', 
        secondary=chef_restaurant_association, 
        lazy='dynamic',
        back_populates='chefs',  # Use back_populates here
    )
    # contents = db.relationship('Content', primaryjoin="and_(Content.associated_id==Chef.id, "
    #                                                   "Content.associated_type=='chef')",
    #                            backref='chef')

    def __repr__(self):
        return f'<Chef {self.name}>'


# Restaurant model
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(30), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    distinction = db.Column(db.Integer, nullable=True)
    style = db.Column(db.String(100), nullable=True)
    res_url = db.Column(db.String(120), nullable = True)
    description = db.Column(db.String(300), nullable = True)
    location = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float(50), nullable=True)
    longitude = db.Column(db.Float(50), nullable=True)
    image_url = db.Column(db.String(120), nullable = True)
    michelin_url = db.Column(db.String(120), nullable=True)
    check_ins = db.relationship('CheckIn', backref='restaurant', lazy=True)
     # Define the relationship with Chef
    chefs = db.relationship(
        'Chef', 
        secondary=chef_restaurant_association, 
        back_populates='restaurants',  # Use back_populates here
    )


    # contents = db.relationship('Content', primaryjoin="and_(Content.associated_id==Restaurant.id, "
    #                                                   "Content.associated_type=='restaurant')",
    #                            backref='restaurant')

    def __repr__(self):
        return f'<Restaurant {self.name}>'



##########################################################################
    ########  ########     ##     ########
       ##     ##         ##          ## 
       ##     ####         ##        ##
       ##     ##             ##      ##
       ##     ########    ###        ##
############################################################################
    
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    followed_id = db.Column(db.Integer)
    followed_type = db.Column(db.String)  # 'user', 'chef', 'restaurant'
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    follower = db.relationship('User', backref='following')


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content_type = db.Column(db.String(50))  # e.g., 'article', 'video'
    url = db.Column(db.String(255))  # URL to the content
    image_url = db.Column(db.String(255))
    associated_id = db.Column(db.Integer)
    associated_type = db.Column(db.String)  # e.g., 'restaurant', 'chef'
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))


    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image_url':self.image_url,
            "url":self.url,
        }
    
    def __repr__(self):
        return f'<Content {self.title}>'
    

# def TopRestaurants(db.model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     location = db.Column(db.String(200), nullable=True)
#     top_url = db.Column(db.String(100), nullable=True)
#     res_url = db.Column(db.String(100), nullable=True)
#     phone = db.Column(db.String(30) nullable=True)
#     rank = db.Column(db.Integer, nullable=False)
#     description = db.Column(db.String(200), nullable=True)
#     image_url = db.Column(db.String(200), nullable=True)


if __name__=="__main__":

    pass
