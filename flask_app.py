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

api.add_resource(HelloWorld, '/')
api.add_resource(Test, '/test')

if __name__ == '__main__':
    app.run(debug=True)