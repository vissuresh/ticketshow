from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import User, Venue

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class VenueForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    submit = SubmitField('Create Venue')

    def validate_location(self, location):
        same_loc = Venue.query.filter_by(location = location.data)
        for venue in same_loc:
            if venue.name == self.name.data:
                raise ValidationError('Venue with same name exists in given location!')

class ShowForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    venue = SelectField(u'Select Venue', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    timing = DateTimeLocalField('Date and Time', validators=[DataRequired()], format="%Y-%m-%dT%H:%M")
    submit = SubmitField('Create Show')
    

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
    submit = SubmitField('Book tickets!')

    def validate_qty(self, qty):
        if(qty.data > self.available):
            raise ValidationError('Quantity greater than the available tickets!')
        
        if(qty.data <=0):
            raise ValidationError('Tickets quantity should be positive!')
        
        if(qty.data>10):
            raise ValidationError('Maximum of 10 tickets per booking!')
                
    def __init__(self, *args, **kwargs):
        self.available = kwargs.pop('available', None)
        super(BookingForm, self).__init__(*args, **kwargs)