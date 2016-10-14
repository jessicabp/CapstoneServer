from flask import Flask
from flask_sslify import SSLify
from flask_restful import Api
import flask_login

from traptracker.api import LineInterface, TrapInterface, AnimalInterface, CatchInterface, AuthInterface

import logging

# Set up flask application with all plugins
app = Flask(__name__)
sslify = SSLify(app)
app.config.from_object('traptracker.config')
api = Api(app)

# Flask Login
loginManager = flask_login.LoginManager()
loginManager.login_view = "login"
loginManager.login_message = "Please log in to access this page"
loginManager.login_message_category = "warning"


class Anonymous(flask_login.AnonymousUserMixin):
    def __init__(self):
        self.username = "Guest"

    def __repr__(self):
        return "<User: {}>".format(self.username)


loginManager.anonymous_user = Anonymous
loginManager.init_app(app)

# Set up logging
logging.basicConfig(
    filename="server.log",
    filemode="a",  # Append
    level=logging.WARN
)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

# Link URL to classes
api.add_resource(LineInterface, "/api/line")
api.add_resource(TrapInterface, "/api/trap")
api.add_resource(CatchInterface, "/api/catch")
api.add_resource(AnimalInterface, "/api/animal")
api.add_resource(AuthInterface, "/api/checkauth")

# Import all routes from web_classes
import traptracker.web_classes