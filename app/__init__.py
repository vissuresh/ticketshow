from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_restful import Resource, Api

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
login = LoginManager(app)
login.login_view = 'login'
my_api = Api(app)

from app import routes, models

from app.api import UserAPI, AuthLoginAPI, AuthLogoutAPI, VenuesAPI, ShowsAPI, SearchVenuesAPI, SearchShowsAPI
my_api.add_resource(UserAPI, "/api/user" ,"/api/user/<int:user_id>")
my_api.add_resource(AuthLoginAPI, "/api/auth/login")
my_api.add_resource(AuthLogoutAPI, "/api/auth/logout")
my_api.add_resource(VenuesAPI, "/api/venues", "/api/venues/<int:venue_id>")
my_api.add_resource(ShowsAPI, "/api/shows", "/api/shows/<int:show_id>")

my_api.add_resource(SearchShowsAPI, "/api/search/shows")
my_api.add_resource(SearchVenuesAPI, "/api/search/venues")
