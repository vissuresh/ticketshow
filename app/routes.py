from app import app,db
from app.forms import LoginForm, RegistrationForm, VenueForm, ShowForm, BookingForm
from flask import render_template, redirect, url_for, flash, request
from app.models import User, Venue, Show, Show_Venue, Booking, Tag
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
        db.session.commit()
        flash("User created Successfully!")
        return redirect(url_for('login'))
    
    return render_template('register.html', title = 'Register', form = form)

@app.route('/create_venue', methods=['GET', 'POST'])
@login_required
@check_admin_decor
def create_venue():
    form = VenueForm()

    if form.validate_on_submit():
        if form.Name_and_location_validation() == False:
            flash("Venue with same name exists in given location!")

        else:
            new_venue = Venue(name = form.name.data, location = form.location.data, capacity = form.capacity.data, caption = form.caption.data)
            db.session.add(new_venue)
            db.session.commit()
            flash("Venue added Successfully!")
        
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

        if form.Name_and_location_validation(except_venue_id=venue_id) == False:
            flash("Venue with same NAME and LOCATION exists!")
            
        else:
            venue.name = form.name.data
            venue.location = form.location.data
            venue.capacity = form.capacity.data
            venue.caption = form.caption.data

            db.session.commit()

            flash('Venue updated successfully!')
        
        return redirect(url_for('manage_venues'))
    
    
    #Pre-populate form values so that user shall change only the necessary fields
    form.process(obj = venue)
    
    flash(warning)
    return render_template('create_venue.html', title = 'Edit Venue', form = form)

@app.route('/delete_venue/<int:venue_id>')
def delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    associated_shows = Show_Venue.query.filter_by(venue_id = venue_id)
    associated_shows.delete()
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
        if form.Name_and_Timing_validation() == False:
            flash("Show with same NAME and TIMING exists!")

        else:
            new_show_obj = Show()
            new_show_obj.set_data(form.data)
            db.session.add(new_show_obj)

            #add venue entries
            for venue in form.venue.data:
                print(venue)
                new_show_obj.venues.append(Venue.query.get(int(venue)))

            
            #add tags 
            tags = set()
            for x in form.tags.data.split(" "):
                tags.add(x.lower())
            #Created Tags set

            for tag in tags:
                new_show_obj.tags.append(Tag(tag=tag))
            #added tags

            try:
                db.session.commit()
                flash("Show added Successfully!")

            except:
                db.session.rollback()
                flash('Unknown Error occured!')

        return redirect(url_for('manage_shows'))

    return render_template('create_show.html', title="Create Show", form = form)


@app.route('/book_show/show<show_id>_venue<venue_id>', methods=['GET','POST'])
@login_required
def book_show(show_id, venue_id):
    show = Show.query.get_or_404(show_id)
    venue = Venue.query.get_or_404(venue_id)
    show_venue = Show_Venue.query.get_or_404((show_id,venue_id))
    
    available = venue.capacity - show_venue.sold

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

    return render_template('book_show.html', title="Book Show", show = show, venue=venue, available = available, form = form)

@app.route('/user_bookings')
@login_required
def user_bookings():
    context = get_booking_info()
        
    return render_template('user_bookings.html', context=context)


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

        if form.Name_and_Timing_validation(except_show_id = show_id) == False:
            flash("Show with same NAME and TIMING exists!")

        else:
            show_to_edit.set_data(form.data)

            selected_form_venue_ids = [i for i in form.venue.data]

            for val in selected_form_venue_ids:
                venue = Venue.query.get(val)
                if venue not in existing_venues:
                    show_to_edit.venues.append(venue)

            for venue in existing_venues:
                if venue.id not in selected_form_venue_ids:
                    show_to_edit.venues.remove(venue)

            show_to_edit.tags.delete()

            #add tags 
            tags = set()
            for x in form.tags.data.split(" "):
                tags.add(x.lower())

            for tag in tags:
                show_to_edit.tags.append(Tag(tag=tag))
            #Added tags

            try:
                db.session.commit()
                flash('Show updated successfully!')

            except:
                db.session.rollback()
                flash('Unknown error occurred')            
        
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