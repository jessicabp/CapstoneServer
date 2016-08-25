from flask import Flask
from flask_restful import Resource, Api
import orm
from orm import Line

app = Flask(__name__)
api = Api(app)

sess = orm.get_session()

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class LineInterface(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass

class TrapInterface(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass


class CatchInterface(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass


api.add_resource(HelloWorld, "/")
api.add_resource(LineInterface, "/line")
api.add_resource(TrapInterface, "/trap")
api.add_resource(CatchInterface, "/catch")

if __name__ == '__main__':
    app.run(debug=True)
