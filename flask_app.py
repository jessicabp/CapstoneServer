from flask import Flask
from flask import request
from flask_restful import Resource, Api
import collections
import hashlib
import os
import binascii
import datetime
import orm
from orm import Line, Trap, Catch

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

        # Error checking for processing data
        if not isinstance(json_data, collections.Iterable):
            return {"error": {
                        "code": 0, # TODO: Change error code
                        "message": "Non iterable type returned"}}

        lines = []
        for line_data in json_data:
            if "id" in line_data: # ID passed, only edit name of new line
                line = sess.query(Line).filter_by(id=line_data['id']).first()
                validate(line_data['id'], line_data['password']) # TODO: Return error if can't validate

                line.name = line_data['name']

            else: # ID isn't passed, create new line
                # Create salt and hash password
                salt = os.urandom(40)
                hashed = hashlib.pbkdf2_hmac('sha1', str.encode(line_data['password']), salt, 100000)

                # Create line and store in database
                line = Line(line_data['name'], binascii.hexlify(hashed).decode("utf-8"), binascii.hexlify(salt))
                lines.append(line)
                sess.add(line)

        sess.commit()
        return {'data': [{'id': line.id, 'name': line.name} for line in lines]}

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
                            'rebait_time': trap.rebait_time.timestamp(),
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

        #validate(line_id, args['password']) # TODO: Return error if can't validate

        if not isinstance(json_data, collections.Iterable):
            return {"error": {
                        "code": 0, # TODO: Change error code
                        "message": "Non iterable type returned"}}

        traps = []
        for trap_data in json_data:
            if "id" in trap_data: # ID passed, edit parameters of trap
                trap = sess.query(Trap).filter_by(id=trap_data['id']).first()

                #Edit values apart of trap
                trap.lat = trap_data['lat']
                trap.long = trap_data['long']
                trap.line_id = trap_data['line_id'] # Don't know if this should be here
                trap.line_order = trap_data['line_order'] # Don't know if this should be here
                trap.path_side = trap_data['path_side'] # Don't know if this should be here
                if "broken" in trap_data:
                    trap.broken = trap_data['broken']
                if "moved" in trap_data:
                    trap.moved = trap_data['moved']

            else: # Trap doesn't exist, create a new trap
                trap = Trap(datetime.date.fromtimestamp(trap_data['rebait_time']),
                            trap_data['lat'],
                            trap_data['long'],
                            trap_data['line_id'],
                            trap_data['line_order'],
                            trap_data['path_side'],
                            )
                traps.append(trap)
                sess.add(trap)

        sess.commit()
        return {'result': [{'id': trap.id,
                            'line_id': trap.line_id,
                            'rebait_time': trap.rebait_time.timestamp(),
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
        args = request.args
        result = sess.query(Catch)
        if 'line_id' in args: result = result.join(Trap.id).filter(Trap.line_id == args['line_id']) # TODO: Test relationship query
        if 'trap_id' in args: result = result.filter_by(id=args['trap_id'])

        return {'result': [{'id': catch.id,
                            'trap_id': catch.trap_id,
                            'animal_id': catch.animal_id,
                            'time': catch.time.timestamp()} for catch in result.all()]}

    def put(self):
        json_data = request.get_json()

        #validate(line_id, args['password']) # TODO: Return error if can't validate

        if not isinstance(json_data, collections.Iterable):
            return {"error": {
                        "code": 0, # TODO: Change error code
                        "message": "Non iterable type returned"}}

        catches = []
        for catch_data in json_data:
            if "id" in catch_data:
                catch = sess.query(Catch).filter_by(id=catch_data['id']).first()

                #Edit values in catch
                catch.trap_id = catch_data['trap_id']
                catch.animal_id = catch_data['animal_id']
                #Not editing time of the catch

            else: # ID not given, create new catch
                catch = Catch(catch_data['trap_id'],
                              catch_data['animal_id'],
                              datetime.date.fromtimestamp(catch_data['time']))
                catches.append(catch)
                sess.add(catch)

        sess.commit()

        return {'result': [{'id': catch.id,
                            'trap_id': catch.trap_id,
                            'animal_id': catch.animal_id,
                            'time': catch.time} for catch in catches]}

    def post(self):
        pass


def validate(line_id, password):
    """
    Validate passwords by compared the line_id

    Keyword arguments:
    line_id -- Line id to compared hashed password stored in database to
    password -- Password to compared hashed password against
    """
    line = sess.query(Line).filter_by(id=line_id).first()
    hash_compare = hashlib.pbkdf2_hmac('sha1', str.encode(password), binascii.unhexlify(line.salt), 100000)

    return binascii.hexlify(hash_compare).decode("utf-8") == line.password_hashed


api.add_resource(LineInterface, "/line")
api.add_resource(TrapInterface, "/trap")
api.add_resource(CatchInterface, "/catch")

if __name__ == '__main__':
    app.run(debug=True)
