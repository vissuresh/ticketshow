from flask_restful import Resource, fields, marshal_with, reqparse, marshal
from flask_login import current_user, login_user, logout_user
from app.models import User, Venue, Show, Tag, Booking
from app.validation import NotFoundError, AccessDeniedError, BusinessValidationError, SchemaValidationError, validate_tags, validate_timing
from flask import request
from app import db
from sqlalchemy.exc import IntegrityError


user_fields = {'id': fields.Integer, 'username': fields.String}
venue_fields = {'id': fields.Integer, 'name': fields.String, 'location':fields.String, 'capacity':fields.Integer, 'caption':fields.String}
show_fields = {'id': fields.Integer, 'name': fields.String, 'price':fields.Integer, 'caption':fields.String, 'timing':fields.DateTime}

user_parser = reqparse.RequestParser()
user_parser.add_argument('username')
user_parser.add_argument('password')

venue_parser = reqparse.RequestParser()
venue_parser.add_argument('name')
venue_parser.add_argument('location')
venue_parser.add_argument('capacity')
venue_parser.add_argument('caption')

show_parser = reqparse.RequestParser()
show_parser.add_argument('name')
show_parser.add_argument('venues',action='append')
show_parser.add_argument('capacity')
show_parser.add_argument('caption')
show_parser.add_argument('timing')
show_parser.add_argument('price')
show_parser.add_argument('tags')

class UserAPI(Resource):

    @marshal_with(user_fields)
    def get(self, user_id):
        if not current_user.is_authenticated:
            raise AccessDeniedError(status_code=401)
    
        user = User.query.get(user_id)
        if user is None:
            raise NotFoundError(status_code = 404)
        
        if current_user.id != user.id:
            raise AccessDeniedError(status_code=403)
        
        return user

    @marshal_with(user_fields)
    def put(self):
        if not current_user.is_authenticated:
            raise AccessDeniedError(status_code=401)
        
        user = User.query.get(current_user.id)
        user.username = request.args.get('username')
        db.session.commit()

        return user

    @marshal_with(user_fields)
    def post(self):

        args = user_parser.parse_args()
        username = args.get('username', None)
        password = args.get('password', None)

        if username is None:
            raise BusinessValidationError(status_code=400, error_code="BE1001", error_message="username is required")
        
        if password is None:
            raise BusinessValidationError(status_code=400, error_code="BE1002", error_message="password is required")
        
        new_user = User(username = username)
        new_user.set_password(password = password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            raise SchemaValidationError(status_code=409, error_code="SE1001", error_message="username already exists")
        
        return new_user,201
    
    
class AuthLoginAPI(Resource):

    def post(self):
        if current_user.is_authenticated:
            raise BusinessValidationError(status_code=409, error_code="BE2001", error_message="user is already logged in")
        
        args = user_parser.parse_args()
        username = args.get('username', None)
        password = args.get('password', None)

        if username is None:
            raise BusinessValidationError(status_code=400, error_code="BE2002", error_message="username is required")
        
        if password is None:
            raise BusinessValidationError(status_code=400, error_code="BE2003", error_message="password is required")

        
        user = User.query.filter_by(username=username).first()

        if user is None:
            raise NotFoundError(status_code=404, error_code="BE2004", error_message="username does not exist")
        
        if not user.check_password(password=password):
            raise BusinessValidationError(status_code=401, error_code="BE2005", error_message="incorrect password")
        
        login_user(user)

        return {},200
    

class AuthLogoutAPI(Resource):

    def get(self):
        if current_user.is_anonymous:
            raise AccessDeniedError(status_code=401)
        
        logout_user()

        return {},200
    

class VenuesAPI(Resource):
    
    @marshal_with(venue_fields)
    def get(self, venue_id):
        try:
            venue = Venue.query.get_or_404(venue_id)
        except:
            raise NotFoundError(status_code=404)
        return venue


    @marshal_with(venue_fields)
    def post(self):
        try:
            if current_user.username != "admin":
                raise AccessDeniedError(status_code=403)
        except:
            raise AccessDeniedError(status_code=401)
        
        args = venue_parser.parse_args()

        if args.get('name',None) is None:
            raise BusinessValidationError(status_code=400, error_code="BE3001", error_message="name is required")
        
        if args.get('location',None) is None:
            raise BusinessValidationError(status_code=400, error_code="BE3002", error_message="location is required")
        
        if args.get('capacity',None) is None:
            raise BusinessValidationError(status_code=400, error_code="BE3003", error_message="capacity is required")
        
        elif int(args.get('capacity')) < 0:
            raise BusinessValidationError(status_code=400, error_code="BE3004", error_message="capacity cannot be negative")

        
        new_venue = Venue()
        new_venue.set_data(args)
        db.session.add(new_venue)
        try:
            db.session.commit()
        except IntegrityError as e:
            raise SchemaValidationError(status_code=409, error_code="SE3001", error_message=str(e.__cause__))
        
        return new_venue,201
    
    @marshal_with(venue_fields)
    def put(self, venue_id):
        try:
            if current_user.username != "admin":
                raise AccessDeniedError(status_code=403)
        except:
            raise AccessDeniedError(status_code=401)

        try:
            venue_to_edit = Venue.query.get_or_404(venue_id)
        except:
            raise NotFoundError(status_code=404)
        
        args = venue_parser.parse_args()
        venue_to_edit.set_data(args)

        try:
            db.session.commit()
        except IntegrityError as e:
            raise SchemaValidationError(status_code=409, error_code="SE3001", error_message=str(e.__cause__))
        
        return venue_to_edit,200
    
    def delete(self, venue_id):
        try:
            if current_user.username != "admin":
                raise AccessDeniedError(status_code=403)
        except:
            raise AccessDeniedError(status_code=401)
        
        try:
            venue_to_delete = Venue.query.get_or_404(venue_id)
        except:
            raise NotFoundError(status_code=404)
        
        db.session.delete(venue_to_delete)
        db.session.commit()

        return {},200
    
class ShowsAPI(Resource):
    
    def get(self, show_id):
        try:
            show = Show.query.get_or_404(show_id)
        except:
            raise NotFoundError(status_code=404)
        
        data = marshal(show, show_fields)
        data['venues'] = [venue.id for venue in show.venues]
        return data
    

    def post(self):
        try:
            if current_user.username != "admin":
                raise AccessDeniedError(status_code=403)
        except:
            raise AccessDeniedError(status_code=401)
        
        args = show_parser.parse_args()

        if args.get('name',None) is None:
            raise BusinessValidationError(status_code=400, error_code="BE4001", error_message="name is required")
        
        if args.get('timing',None) is None:
            raise BusinessValidationError(status_code=400, error_code="BE4002", error_message="timing is required")

        if args.get('price',None) is None:
            raise BusinessValidationError(status_code=400, error_code="BE4003", error_message="price is required")
        

        # Validating timing
        timing = args.get('timing')
        if timing:
            timing, error_message = validate_timing(timing)

            if error_message:
                raise BusinessValidationError(status_code = 400, error_code="BE4004", error_message=error_message)
            args['timing'] = timing

        
        new_show = Show()

        venues = args.get('venues',None)
        if venues is not None:
            venues = list(map(int, venues))
            for venue_id in venues:
                try:
                    venue = Venue.query.get_or_404(venue_id)
                except:
                    raise NotFoundError(status_code=404, error_code="BE4005", error_message="venue id {} does not exist".format(venue_id))
                new_show.venues.append(venue)


        # Validating and adding tags
        new_tags = args.get('tags', None)
        if new_tags:
            tags_error = validate_tags(new_tags)
            if tags_error:
                raise BusinessValidationError(status_code=400, error_code="BE4006", error_message=tags_error)
            
            #add tags 
            tags = set()
            for x in new_tags.split(" "):
                if x!='':
                    tags.add(x.lower())

            for tag in tags:
                new_show.tags.append(Tag(tag=tag))
            #Added tags
        

        # Setting and adding new show to DB
        new_show.set_data(args)
        db.session.add(new_show)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise SchemaValidationError(status_code=409, error_code="SE4001", error_message=str(e.__cause__))
        
        data = marshal(new_show, show_fields)
        data['venues'] = venues
        data['tags'] = [tag.tag for tag in new_show.tags]
        
        return data,201
    

    def put(self, show_id):
        try:
            if current_user.username != "admin":
                raise AccessDeniedError(status_code=403)
        except:
            raise AccessDeniedError(status_code=401)

        try:
            show_to_edit = Show.query.get(show_id)
        except:
            raise NotFoundError(status_code=404)
        
        args = show_parser.parse_args()
        timing = args.get('timing')

        # Validating timing
        if timing:
            timing, error_message = validate_timing(timing)

            if error_message:
                raise BusinessValidationError(status_code = 400, error_code="BE4007", error_message=error_message)
            
            args['timing'] = timing

        
        show_to_edit.set_data(args)

        # Creating a Deep Copy of existing venues
        existing_venues = []
        for venue in show_to_edit.venues:
            existing_venues.append(venue)

        # Adding venues that are new
        new_venues = args.get('venues',None)
        if new_venues is not None:
            new_venues = list(map(int, new_venues))
            for venue_id in new_venues:
                print(venue_id, type(venue_id))
                venue = Venue.query.get(venue_id)
                if venue not in show_to_edit.venues:
                    show_to_edit.venues.append(venue)

        # Removing existing venues that are not specified
        for venue in existing_venues:
            if venue.id not in new_venues:
                bookings = Booking.query.filter_by(show_id=show_id, venue_id = venue.id)
                bookings.delete()
                show_to_edit.venues.remove(venue)

        
        # Validating and setting tags
        new_tags = args.get('tags',None)

        if new_tags:
            tags_error = validate_tags(new_tags)
            if tags_error:
                raise BusinessValidationError(status_code = 400, error_code="BE4008", error_message=tags_error)
            

            show_to_edit.tags.delete()

            #add tags 
            tags = set()
            for x in new_tags.split(" "):
                if x!='':
                    tags.add(x.lower())

            for tag in tags:
                show_to_edit.tags.append(Tag(tag=tag))
            #Added tags


        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise SchemaValidationError(status_code=409, error_code="SE4001", error_message=str(e.__cause__))
        
        data = marshal(show_to_edit, show_fields)
        data['venues'] = [venue.id for venue in show_to_edit.venues]
        data['tags'] = [tag.tag for tag in show_to_edit.tags]
            
        
        return data,200
    
    def delete(self, show_id):
        try:
            if current_user.username != "admin":
                raise AccessDeniedError(status_code=403)
        except:
            raise AccessDeniedError(status_code=401)
        
        try:
            show_to_delete = Show.query.get(show_id)
        except:
            raise NotFoundError(status_code=404)
        
        db.session.delete(show_to_delete)
        db.session.commit()

        return {},200
    

class SearchVenuesAPI(Resource):

    @marshal_with(venue_fields, envelope='venues')
    def get(self):   
        args = request.args
        name = args.get('name', None)
        location = args.get('location', None)

        venues = Venue.query
        if name:
            venues = venues.filter(Venue.name.like("%"+name+"%"))
        if location:
            venues = venues.filter(Venue.location.like("%"+location+"%"))

        return venues.all(),200
    

class SearchShowsAPI(Resource):

    @marshal_with(show_fields, envelope='shows')
    def get(self):   
        args = request.args
        name = args.get('name', None)
        from_timing = args.get('from_datetime', None)
        till_timing = args.get('till_datetime', None)    
        min_price = args.get('min_price', None)
        max_price = args.get('max_price', None) 
        tag = args.get('tag', None)

        shows = Show.query
        if name:
            shows = shows.filter(Show.name.like("%"+name+"%"))

        if from_timing:
            from_timing, error_message = validate_timing(from_timing)
            if error_message:
                raise BusinessValidationError(status_code=400, error_code="BE5001", error_message=error_message)
            
            shows = shows.filter(Show.timing >= from_timing)

        if till_timing:
            till_timing, error_message = validate_timing(till_timing)
            if error_message:
                raise BusinessValidationError(status_code=400, error_code="BE5001", error_message=error_message)
            
            shows = shows.filter(Show.timing <= till_timing)

        if min_price:
            shows = shows.filter(Show.price >= min_price)
        
        if max_price:
            shows = shows.filter(Show.price <= max_price)

        if tag:
            tag = tag.lower()
            shows = shows.filter(Show.tags.any(Tag.tag==tag))

        return shows.all(),200