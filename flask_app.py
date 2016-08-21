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

class Test(Resource):
    def get(self):
        return str(sess.query(Line).all())

    def put(self):
        pass

    def post(self):
        pass


class Trap(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass


class Catch(Resource):
    def get(self):
        pass

    def put(self):
        pass

    def post(self):
        pass


class Check(Resource):
    def get(self):
        pass

api.add_resource(HelloWorld, "/")
api.add_resource(Test, "/test")
api.add_resource(Trap, "/trap")
api.add_resource(Catch, "/catch")
api.add_resource(Check, "/check")

if __name__ == '__main__':
    app.run(debug=True)
