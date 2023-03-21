from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateTimeLocalField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import User, Venue, Show
import datetime

class SelectMultipleField(SelectMultipleField):
    def process_formdata(self, valuelist):
        self.data = [int(x) for x in valuelist]

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class VenueForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    caption = TextAreaField('Caption (optional)')
    submit = SubmitField('Submit')

    def Name_and_location_validation(self, except_venue_id = None):
        if except_venue_id is None:
            exist = Venue.query.filter_by(name = self.name.data, location = self.location.data).first()

        else:
            exist = Venue.query.filter(Venue.id != except_venue_id).filter_by(name = self.name.data, location = self.location.data).first()

        if exist is not None:
            return False
        return True

class ShowForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired()])
    caption = TextAreaField('Caption (optional)')
    venue = SelectMultipleField('Select Venue(s)', validators=[DataRequired()])
    timing = DateTimeLocalField('Date and Time', validators=[DataRequired()], format="%Y-%m-%dT%H:%M")
    price = IntegerField('Price', validators=[DataRequired()])
    tags = TextAreaField('Tags (optional)')
    submit = SubmitField('Submit')

    def validate_tags(self, tags):
        import string
        
        for tag in tags.data.split(' '):
            if len(tag) > 16:
                raise ValidationError('Length of tag must be <= 16')
            
            for c in tag:
                if c in string.punctuation:
                    raise ValidationError('Tags cannot contain punctuation')

    def validate_timing(self, timing):
        if timing.data <= datetime.datetime.now():
            raise ValidationError('Error 404: Time Machine not found :( ')
        
    def Name_and_Timing_validation(self, except_show_id = None):
        exist = Show.query.filter_by(name = self.name.data, timing = self.timing.data)

        if except_show_id is not None:
            exist = exist.filter(Show.id != except_show_id)

        exist = exist.first()

        if exist is None:
            return True
        return False
    
    

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Re-enter Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError('Username exists!')
        

class BookingForm(FlaskForm):
    qty = IntegerField('Quantity', validators=[DataRequired()])
    available = None
    submit = SubmitField('Book tickets!')

    def validate_qty(self, qty):
        if(qty.data > self.available):
            raise ValidationError('Quantity greater than the available tickets!')
        
        if(qty.data <=0):
            raise ValidationError('Tickets quantity should be positive!')
        
        if(qty.data>10):
            raise ValidationError('Maximum of 10 tickets per booking!')