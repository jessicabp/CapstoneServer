from flask import Flask
from flask_sslify import SSLify
from flask_googlemaps import GoogleMaps
from flask_restful import Api
import flask_login

from traptracker.api import LineInterface, TrapInterface, AnimalInterface, CatchInterface
from traptracker.auth import Anonymous

import logging
import base64

# Set up flask application with all plugins
app = Flask(__name__)
sslify = SSLify(app)
app.config["SECRET_KEY"] = b"w-X\xc2\xd3\xd3\xbd{+\x01\x82\xb0\x83'\xe0Dyk\xab\x98V\xf9\x1e}"
api = Api(app)

# Google Maps
app.config['GOOGLEMAPS_KEY'] = "AIzaSyBcOWrE3u1z01r0XSysaZhQq_G1oz0oJps"
GoogleMaps(app)

# Flask Login
loginManager = flask_login.LoginManager()
loginManager.login_view = "login"
loginManager.login_message = "Please log in to access this page"
loginManager.login_message_category = "warning"
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

# Import all routes from web_classes
import traptracker.web_classes