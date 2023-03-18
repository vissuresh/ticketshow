from app import app,db
from app.forms import LoginForm, RegistrationForm, VenueForm, ShowForm, BookingForm
from flask import render_template, redirect, url_for, flash, request
from app.models import User, Venue, Show, Booking
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

def check_admin_decor(my_route):

    def wrapper_func(*args, **kwargs):

        if current_user.username != "admin":
            flash("Access denied. No admin privileges for {}".format(current_user.username))
            return redirect(url_for('index'))
        else:
            return my_route(*args, **kwargs)
        
    wrapper_func.__name__ = my_route.__name__
    return wrapper_func


def get_booking_info():
    my_bookings = current_user.bookings
    data_dic = {}

    for booking in my_bookings:
        if data_dic.get(booking.id) is None:
            data_dic[booking.id] = {}

        data_dic[booking.id]['show'] = Show.query.get(booking.show_id)
        data_dic[booking.id]['venue'] = Venue.query.get(booking.venue_id)
        data_dic[booking.id]['booking_info'] = booking

    return data_dic


@app.route('/')
@app.route('/index')
@login_required
def index():

    return render_template('index.html', title="Home", context = Venue.query.all())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You're already logged in.")
        return redirect(url_for('/index'))
    
    form = LoginForm() 
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and user.check_password(password = form.password.data):
            login_user(user, remember = form.remember_me.data)
            nextpage = request.args.get('next')
            if not nextpage or url_parse(nextpage).netloc !='':
                return redirect(url_for('index'))
            return redirect(nextpage)
        
        else:
            flash('Invalid username or password!')
            return redirect(url_for('login'))

    return render_template('login.html', title = 'Login', form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You're already logged in.")
        return redirect(url_for('index'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(username = form.username.data)
        new_user.set_password(password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("User created Successfully!")
        return redirect(url_for('login'))
    
    return render_template('register.html', title = 'Register', form = form)

@app.route('/add_venue', methods=['GET', 'POST'])
@login_required
@check_admin_decor
def add_venue():
    
    form = VenueForm()

    if form.validate_on_submit():
        new_venue = Venue(name = form.name.data, location = form.location.data, capacity = form.capacity.data)
        db.session.add(new_venue)
        db.session.commit()
        flash("Venue added Successfully!")
        return redirect(url_for('add_venue'))
    
    return render_template('add_venue.html', title = 'Add Venue', form = form)

@app.route('/add_show', methods=['GET','POST'])
@login_required
@check_admin_decor
def add_show():

    form = ShowForm()
    venues = []
    for venue in Venue.query.all():
        venues.append((venue.id,'{}, {}'.format(venue.name, venue.location)))
    form.venue.choices=venues

    if form.validate_on_submit():

        new_show = Show(name = form.name.data, venue_id = int(form.venue.data))
        new_show.price = form.price.data

        new_show.timing = form.timing.data

        db.session.add(new_show)
        db.session.commit()
        flash("Show added Successfully!")
        return redirect(url_for('add_show'))

    return render_template('add_show.html', title="Add Show", form = form)


@app.route('/book_show/<show_id>', methods=['GET','POST'])
@login_required
def book_show(show_id):
    show = Show.query.get(show_id)
    venue = Venue.query.get(show.venue_id)
    total_booked=0
    for booking in show.bookings:
        total_booked += booking.qty

    available = venue.capacity - total_booked

    form = BookingForm(available=available)

    if form.validate_on_submit():
        new_booking = Booking(user_id = current_user.id, venue_id = venue.id, show_id = show.id, qty = form.qty.data)

        db.session.add(new_booking)
        db.session.commit()

        flash("Booking Success!")
        return redirect(url_for('book_show', show_id=show_id))

    return render_template('book_show.html', title="Book Show", show = show, venue=venue, available = available, form = form)

@app.route('/user_bookings', methods = ['GET', 'POST'])
@login_required
def user_bookings():
    context = get_booking_info()
    for item in context.items:
        print(item)
        
    return render_template('user_bookings.html', context = context)
