from flask import Flask
from flask_googlemaps import GoogleMaps
from flask_restful import Api
import logging
import web_classes as wb
from api import LineInterface, TrapInterface, AnimalInterface, CatchInterface

# Set up flask application with all plugins
app = Flask(__name__)
app.config["SECRET_KEY"] = b"w-X\xc2\xd3\xd3\xbd{+\x01\x82\xb0\x83'\xe0Dyk\xab\x98V\xf9\x1e}"
api = Api(app)

# Google Maps
app.config['GOOGLEMAPS_KEY'] = "AIzaSyBcOWrE3u1z01r0XSysaZhQq_G1oz0oJps"
GoogleMaps(app)

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


@app.route("/", methods=["GET"])
def index():
    return wb.index()


@app.route("/create", methods=["GET", "POST"])
def create():
    return wb.createLine()


@app.route("/about", methods=["GET"])
def about():
    return wb.about()


@app.route("/login", methods=["GET", "POST"])
def login():
    return wb.login()


@app.route("/catches/<int:number>", methods=["GET"])
def catches(number):
    return wb.catches(number)


@app.route("/edit/<int:number>", methods=["GET"])
def edit(number):
    return wb.traps(number)


@app.route("/export/<int:number>", methods=["GET"])
def export(number):
    return wb.export(number)


if __name__ == '__main__':
    app.run(debug=True)