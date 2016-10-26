from flask import Flask
from flask_sslify import SSLify
from flask_restful import Api

from traptracker.api import LineInterface, TrapInterface, AnimalInterface, CatchInterface, AuthInterface
import traptracker.orm as orm
from traptracker.orm import Animal

import logging

# Set up flask application with all plugins
app = Flask(__name__)
sslify = SSLify(app)
app.config.from_object('traptracker.config')
api = Api(app)

# Set up logging
logging.basicConfig(
    filename="server.log",
    filemode="a",  # Append
    level=logging.WARN
)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)

# Set up empty
sess = orm.get_session()
try:
    empty = Animal("Empty")
    empty.id = 0
    sess.add(empty)
    sess.commit()
except Exception:
    pass
finally:
    sess.close()

# Link URL to classes
api.add_resource(LineInterface, "/api/line")
api.add_resource(TrapInterface, "/api/trap")
api.add_resource(CatchInterface, "/api/catch")
api.add_resource(AnimalInterface, "/api/animal")
api.add_resource(AuthInterface, "/api/checkauth")

# Import all routes from web_classes
import traptracker.web_classes