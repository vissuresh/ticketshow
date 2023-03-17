from app import db, login
import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

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
    capacity = db.Column(db.Integer)

    shows = db.relationship('Show', backref = 'venue', lazy = 'dynamic')

    def __repr__(self):
        return '<Name: {}, Location: {}, Capacity: {}'.format(self.name, self.location, self.capacity)
    
class Show(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    timing = db.Column(db.DateTime, index = True)
    price = db.Column(db.Integer)
    no_sold = db.Column(db.Integer)
    tags = db.Column(db.String(64), index = True)
    rating = db.Column(db.Float)

    bookings = db.relationship('Booking', backref = 'show', lazy = 'dynamic')

    def __repr__(self):
        return 'Name: {}, Venue: {}, Timing: {}, Price: {}'.format(self.name, Venue.query.get(self.venue_id).name, self.price)
    
    
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    qty = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.datetime.now)
    rating = db.Column(db.Float)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))