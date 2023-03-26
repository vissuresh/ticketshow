from app import db, login
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True, unique = True)
    password_hash = db.Column(db.String(128))

    bookings = db.relationship('Booking', backref = 'user', lazy = 'dynamic')

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
    pic = db.Column(db.LargeBinary)

    shows = db.relationship('Show', secondary = 'show_venue', backref = 'venues', lazy = 'dynamic')
    bookings = db.relationship('Booking', backref = 'venue', cascade = 'all, delete')

    __table_args__ = (UniqueConstraint('name', 'location', name='u_venue_name_loc'),)

    def set_data(self, data):
        self.name = data['name']
        self.caption = data['caption']
        self.location = data['location']
        self.capacity = data['capacity']
        if(data['pic'].filename != ''):
            self.pic = data['pic'].read()

    def __repr__(self):
        return '<Name: {}, Location: {}>'.format(self.name, self.location)
    
    
class Show(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True)
    caption = db.Column(db.String(128))
    timing = db.Column(db.DateTime, index = True)
    price = db.Column(db.Integer)
    pic = db.Column(db.LargeBinary)

    tags = db.relationship('Tag', backref = 'show', lazy = 'dynamic', cascade = 'all, delete')
    bookings = db.relationship('Booking', backref = 'show', lazy = 'dynamic', cascade = 'all, delete')

    __table_args__ = (UniqueConstraint('name', 'timing', name='u_venue_name_loc'),)

    def set_data(self, data):
        self.name = data['name']
        self.caption = data['caption']
        self.timing = data['timing']
        self.price = data['price']
        if(data['pic'].filename != ''):
            self.pic = data['pic'].read()

    def __repr__(self):
        return 'Name: {}'.format(self.name)
    
class Show_Venue(db.Model):
    __tablename__ = 'show_venue'
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), primary_key = True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key = True)
    sold = db.Column(db.Integer, default = 0)

    __table_args__ = (UniqueConstraint('show_id', 'venue_id', name='u_show_venue'),)

    
class Tag(db.Model):
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), primary_key = True)
    tag = db.Column(db.String(16), primary_key = True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))

    qty = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.now)
    rating = db.Column(db.Float)

    def __repr__(self):
        return 'id: {} Show: {} Venue: {}'.format(self.id, self.show, self.venue)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))