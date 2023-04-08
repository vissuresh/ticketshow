from app import db, login
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), unique = True, nullable = False)
    password_hash = db.Column(db.String(128) , nullable = False)

    bookings = db.relationship('Booking', backref = 'user', lazy = 'dynamic')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True, nullable = False)
    location = db.Column(db.String(64), index = True, nullable = False)
    caption = db.Column(db.String(128))
    capacity = db.Column(db.Integer, nullable = False)
    pic = db.Column(db.LargeBinary)

    shows = db.relationship('Show', secondary = 'show_venue', backref = 'venues', lazy = 'dynamic')
    bookings = db.relationship('Booking', backref = 'venue', cascade = 'all, delete')

    __table_args__ = (UniqueConstraint('name', 'location', name='u_venue_name_loc'),)

    def set_data(self, data):
        if data.get('name'):
            self.name = data['name']

        if data.get('caption'):    
            self.caption = data['caption']

        if data.get('location'):
            self.location = data['location']

        if data.get('capacity'):
            self.capacity = data['capacity']


        if(data.get('pic')):
            if(data['pic'].filename != ''):
                self.pic = data['pic'].read()

    def __repr__(self):
        return '<Name: {}, Location: {}>'.format(self.name, self.location)
    
    
class Show(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), index = True, nullable = False)
    caption = db.Column(db.String(128))
    timing = db.Column(db.DateTime, index = True, nullable = False)
    price = db.Column(db.Integer, index = True, nullable = False)
    rating = db.Column(db.Integer, nullable = True)
    rated_bookings = db.Column(db.Integer, default = 0)
    pic = db.Column(db.LargeBinary)

    tags = db.relationship('Tag', backref = 'show', lazy = 'dynamic', cascade = 'all, delete')
    bookings = db.relationship('Booking', backref = 'show', lazy = 'dynamic', cascade = 'all, delete')

    __table_args__ = (UniqueConstraint('name', 'timing', name='u_show_name_timing'),)

    def set_data(self, data):
        if data.get('name'):
            self.name = data['name']

        if data.get('caption'):    
            self.caption = data['caption']

        if data.get('capacity'):    
            self.capacity = data['capacity']

        if data.get('timing'):
            self.timing = data['timing']

        if data.get('price'):
            self.price = data['price']

        if(data.get('pic')):
            if(data['pic'].filename != ''):
                self.pic = data['pic'].read()

    def update_rating(self, rating):
        if self.rated_bookings ==0 or self.rated_bookings is None:
            self.rated_bookings =1
            self.rating = rating

        else:
            prev_sum = self.rating * self.rated_bookings
            self.rated_bookings +=1
            self.rating = (prev_sum +rating) / self.rated_bookings
            self.rating = round(self.rating,1)
            

    def __repr__(self):
        return 'Name: {}'.format(self.name)
    
class Show_Venue(db.Model):
    __tablename__ = 'show_venue'
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), primary_key = True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key = True)
    sold = db.Column(db.Integer, default = 0, nullable = False)

    __table_args__ = (UniqueConstraint('show_id', 'venue_id', name='u_show_venue'),)

    
class Tag(db.Model):
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), primary_key = True)
    tag = db.Column(db.String(16), primary_key = True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))

    qty = db.Column(db.Integer, nullable = False)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.now, nullable = False)
    rating = db.Column(db.Float)

    def __repr__(self):
        return 'id: {} Show: {} Venue: {}'.format(self.id, self.show, self.venue)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))