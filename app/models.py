from app import db, login
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

show_venue = db.Table('show_venue',
    db.Column('show_id', db.Integer, db.ForeignKey('show.id')),
    db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'))
)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True, unique = True)
    password_hash = db.Column(db.String(128))

    bookings = db.relationship('Booking', backref = 'customer', lazy = 'dynamic')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True)
    location = db.Column(db.String(64), index = True)
    caption = db.Column(db.String(128))
    capacity = db.Column(db.Integer)

    shows = db.relationship('Show', secondary = 'show_venue', backref = 'venues')

    def __repr__(self):
        return '<Name: {}, Location: {}'.format(self.name, self.location)
    
class Tag(db.Model):
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), primary_key = True)
    tag = db.Column(db.String(16), primary_key = True)
    
class Show(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True)
    caption = db.Column(db.String(128))
    timing = db.Column(db.DateTime, index = True)
    price = db.Column(db.Integer)
    no_sold = db.Column(db.Integer)
    
    rating = db.Column(db.Float)

    tags = db.relationship('Tag', backref = 'show', lazy = 'dynamic')

    bookings = db.relationship('Booking', backref = 'show', lazy = 'dynamic')

    def __repr__(self):
        return 'Name: {}'.format(self.name)
    
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    qty = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.datetime.now)
    rating = db.Column(db.Float)

    def __repr__(self):
        return 'id: {}\nShow: {}\nVenue: {}'.format(self.id, Show.query.get(self.show_id))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))