from flask import Flask
from flask import request
from flask_restful import Resource, Api
import orm
from orm import Line

app = Flask(__name__)
api = Api(app)

sess = orm.get_session()

class LineInterface(Resource):
    def get(self):
        args = request.args
        result = sess.query(Line)
        if 'line_id' in args: result = result.filter_by(id=args['line_id'])
        if 'name' in args: result = result.filter_by(name=args['name'])
        return {'result': [{'id': line.id, 'name': line.name} for line in result.all()]}

    def put(self):
        json_data = request.get_json()
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

api.add_resource(LineInterface, "/line")
api.add_resource(TrapInterface, "/trap")
api.add_resource(CatchInterface, "/catch")

if __name__ == '__main__':
    app.run(debug=True)
