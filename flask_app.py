from flask import Flask
from flask import request
from flask_restful import Resource, Api
import collections
import hashlib
import binascii
import orm
from orm import Line, Trap

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
        # TODO: add security layer to PUT /line
        # TODO: add ability to edit existing if "id" is given in a line
        # TODO: handle errors

        if not isinstance(json_data, collections.Iterable):
            pass # TODO: Handle non-iterable error

        lines = []
        for line_data in json_data:
            hashed = hashlib.pbkdf2_hmac('sha1', str.encode(line_data['password']), b'salt', 100000)
            line = Line(line_data['name'], binascii.hexlify(hashed).decode("utf-8"))
            lines.append(line)
            sess.add(line)
        sess.commit()
        return {'result': [{'id': line.id, 'name': line.name} for line in lines]}

    def post(self):
        pass

class TrapInterface(Resource):
    def get(self):
        args = request.args
        result = sess.query(Trap)
        if 'line_id' in args: result = result.filter_by(line_id=args['line_id'])
        if 'trap_id' in args: result = result.filter_by(id=args['trap_id'])
        # consider moving this formatting to a method in Trap
        return {'result': [{'id': trap.id,
                            'line_id': trap.line_id,
                            'rebait_time': trap.rebait_time,
                            'lat': trap.lat,
                            'long': trap.long,
                            'line_order': trap.line_order,
                            'path_side': trap.path_side,
                            'broken': trap.broken,
                            'moved': trap.moved}
                            for trap in result.all()]}

    def put(self):
        json_data = request.get_json()
        # TODO: add security layer to PUT /trap
        # TODO: add ability to edit existing if "id" is given in a trap
        # TODO: handle errors

        if not isinstance(json_data, collections.Iterable):
            pass  # TODO: Handle non-iterable error

        traps = []
        for trap_data in json_data:
            trap = Trap(trap_data['rebait_time'],
                        trap_data['lat'],
                        trap_data['long'],
                        trap_data['line_id'],
                        trap_data['line_order'],
                        trap_data['path_side'],
                        trap_data['broken'],
                        trap_data['moved'])
            traps.append(trap)
            sess.add(trap)

        sess.commit()
        return {'result': [{'id': trap.id,
                            'line_id': trap.line_id,
                            'rebait_time': trap.rebait_time,
                            'lat': trap.lat,
                            'long': trap.long,
                            'line_order': trap.line_order,
                            'path_side': trap.path_side,
                            'broken': trap.broken,
                            'moved': trap.moved} for trap in traps]}

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
