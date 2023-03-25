from app import app,db
from app.forms import LoginForm, RegistrationForm, VenueForm, ShowForm, BookingForm, SearchForm
from flask import render_template, redirect, url_for, flash, request, abort
from app.models import User, Venue, Show, Show_Venue, Booking, Tag
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from sqlalchemy.exc import IntegrityError
import datetime

def check_admin_decor(my_route):

    def wrapper_func(*args, **kwargs):

        if current_user.username != "admin":
            flash("Access denied. No admin privileges for {}".format(current_user.username))
            return redirect(url_for('index'))
        else:
            return my_route(*args, **kwargs)
        
    wrapper_func.__name__ = my_route.__name__
    return wrapper_func


@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
@login_required
def index():
    form = SearchForm()
    if form.validate_on_submit():
        return form.data
    return render_template('index.html', title = "Search", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You're already logged in.")
        return redirect(url_for('index'))
    
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
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Error: Username exists!")
        except:
            db.session.rollback()
            flash('Unknown error occurred!')
        else:
            flash("User created Successfully!")
            return redirect(url_for('login'))
    
    return render_template('register.html', title = 'Register', form = form)

@app.route('/create_venue', methods=['GET', 'POST'])
@login_required
@check_admin_decor
def create_venue():
    form = VenueForm()

    if form.validate_on_submit():
        new_venue = Venue()
        new_venue.set_data(form.data)
        db.session.add(new_venue)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Venue with same name and location EXISTS')
        else:
            flash("Venue created Successfully!")
        
        return redirect(url_for('manage_venues'))
    
    return render_template('create_venue.html', title = 'Create Venue', form = form)


@app.route('/edit_venue/<int:venue_id>', methods = ['GET','POST'])
@login_required
@check_admin_decor
def edit_venue(venue_id):
    warning = 'Note: Making changes to capacity will only be reflected in future bookings.'
    venue = Venue.query.get_or_404(venue_id)
    form = VenueForm()

    if form.validate_on_submit():
        venue.set_data(form.data)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Venue with same name and location EXISTS')
        else:
            flash("Venue updated Successfully!")
        
        return redirect(url_for('manage_venues'))
    
    #Pre-populate form values so that user shall change only the necessary fields
    form.process(obj = venue)
    
    flash(warning)
    return render_template('create_venue.html', title = 'Edit Venue', form = form)

@app.route('/delete_venue/<int:venue_id>')
def delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue deleted successfully')

    return redirect(url_for('manage_venues'))


@app.route('/create_show', methods=['GET','POST'])
@login_required
@check_admin_decor
def create_show():

    form = ShowForm()

    #Choices for venues
    venue_choices = []
    for venue in Venue.query.all():
        venue_choices.append((venue.id,'{}, {}'.format(venue.name, venue.location)))
    form.venue.choices = venue_choices
    #Created choices


    if form.validate_on_submit():
        new_show_obj = Show()
        new_show_obj.set_data(form.data)

        db.session.add(new_show_obj)

        #add venue entries
        for venue in form.venue.data:
            new_show_obj.venues.append(Venue.query.get(int(venue)))

        #add tags 
        tags = set()
        for x in form.tags.data.split(" "):
            if x!= '':
                tags.add(x.lower())
        for tag in tags:
            new_show_obj.tags.append(Tag(tag=tag))
        #added tags

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Show with same name and timing EXISTS')
        else:
            flash("Show created Successfully!")

        return redirect(url_for('manage_shows'))

    return render_template('create_show.html', title="Create Show", form = form)


@app.route('/edit_show/<int:show_id>', methods=['GET','POST'])
@login_required
@check_admin_decor
def edit_show(show_id):
    show_to_edit = Show.query.get_or_404(show_id)

    #Find existing venues
    existing_venues = show_to_edit.venues

    form = ShowForm()

    #Choices for venues
    venue_choices = []
    for venue in Venue.query.all():
        venue_choices.append((venue.id, '{}, {}'.format(venue.name, venue.location) ))
    form.venue.choices = venue_choices
    #Created choices
    

    if form.validate_on_submit():
        show_to_edit.set_data(form.data)
        selected_form_venue_ids = [i for i in form.venue.data]

        for val in selected_form_venue_ids:
            venue = Venue.query.get(val)
            if venue not in show_to_edit.venues:
                show_to_edit.venues.append(venue)

        for venue in existing_venues:
            if venue.id not in selected_form_venue_ids:
                show_to_edit.venues.remove(venue)

        show_to_edit.tags.delete()

        #add tags 
        tags = set()
        for x in form.tags.data.split(" "):
            if x!='':
                tags.add(x.lower())

        for tag in tags:
            show_to_edit.tags.append(Tag(tag=tag))
        #Added tags

        try:
            db.session.commit()
            flash('Show updated successfully!')

        except IntegrityError:
            db.session.rollback()
            flash('Show with same name and timing EXISTS!')            
        
        return redirect(url_for('manage_shows'))
        
    form.process(obj = show_to_edit)

    #Get existing tags to prefill form
    existing_tags = ""
    for tag_obj in show_to_edit.tags:
        existing_tags += tag_obj.tag + " "
    form.tags.data = existing_tags
    
    return render_template('create_show.html', title = 'Edit Show', form = form, existing_venues=existing_venues)

@app.route('/delete_show/<show_id>')
@login_required
@check_admin_decor
def delete_show(show_id):
    show_to_delete = Show.query.get_or_404(show_id)
    db.session.delete(show_to_delete)
    db.session.commit()

    flash('Show deleted successfully!')
    return redirect((url_for('manage_shows')))


@app.route('/book_show/show<show_id>_venue<venue_id>', methods=['GET','POST'])
@login_required
def book_show(show_id, venue_id):
    show_venue = Show_Venue.query.get_or_404((show_id,venue_id))
    show = Show.query.get(show_id)
    venue = Venue.query.get(venue_id)

    form = BookingForm()
    form.available = venue.capacity - show_venue.sold

    if form.validate_on_submit():
        new_booking = Booking(user_id = current_user.id, venue_id = venue_id, show_id = show_id, qty = form.qty.data)

        show_venue.sold += form.qty.data
        db.session.add(new_booking)

        try:
            db.session.commit()
            flash("Booking Success!")
        except:
            db.session.rollback()
            flash('Unknown error occurred')
        return redirect(url_for('book_show', show_id=show_id, venue_id = venue_id))

    return render_template('book_show.html', title="Book Show", show=show, venue=venue, form = form)


@app.route('/cancel_booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(404)

    if(booking.show.timing < datetime.datetime.now()):
        flash("This show has passed!")
    else:
        show_venue = Show_Venue.query.get((booking.show_id, booking.venue_id))
        show_venue.sold -= booking.qty
        db.session.delete(booking)
        try:
            db.session.commit()
            flash('Booking CANCELLED')
        except:
            flash('Unknown error occurred')
            db.session.rollback() 
    return redirect(url_for('user_bookings'))
    

@app.route('/user_bookings', methods = ['GET','POST'])
@login_required
def user_bookings():

    if request.method=='POST':
        booking = Booking.query.get(int(request.form['booking_id']))
        booking.rating = float(request.form['rating'])

        try:
            db.session.commit()
            flash('Rating updated for booking ID {}'.format(booking.id))
        except:
            flash('Unknown error occurred')
            db.session.rollback()

        return redirect(url_for('user_bookings'))
    
    return render_template('user_bookings.html', bookings = current_user.bookings, now = datetime.datetime.now())


@app.route('/manage_venues')
@login_required
@check_admin_decor
def manage_venues():
    return render_template('manage_venues.html', title = 'Manage Venues', venues = Venue.query.all())


@app.route('/manage_shows')
@login_required
@check_admin_decor
def manage_shows():
    return render_template('manage_shows.html', title = 'Manage Shows', shows = Show.query.all())