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
        """
        /line GET request will return lines in JSON format back to the user

        Filters (Optional):
        - line_id=<int> : filters results by id given
        - name=<string> : filters results by searching for substring

        Returned:
        - JSONObject: {'result': [line...]}
        - Line Object: {'id': <int>,
                        'name': <string>}

        """
        args = request.args
        result = sess.query(Line)
        if 'line_id' in args: result = result.filter_by(id=args['line_id'])
        if 'name' in args: result = result.filter_by(name=args['name'])
        return {'result': [line.getDict() for line in result.all()]}

    def put(self):
        """
        /line PUT request will write or edit line objects into the database

        Input:
        - JSONArray: [line...]
        - Line Object: {'id': <int>, (Optional: if given, overrides set in database. If excluded, creates new line)
                        'name': <string>,
                        'password': <string>}
        """

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
                authenticate(line_data['id'], line_data['password']) # TODO: Return error if can't validate

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
        return {'data': [line.getDict() for line in lines]}

    def delete(self):
        """
        /line DELETE request will delete lines in the database

        """

        pass


class TrapInterface(Resource):
    def get(self):
        """
        /trap GET request will return traps in JSON format back to the user

        Filters (Optional):
        - line_id=<int> : filters results by line id given
        - trap_id=<int> : filters results by trap id given

        Returned:
        - JSONObject: {'result': [trap...]}
        - Trap Object: {'id': <int>,
                        'line_id': <int>,
                        'rebait_time': <long int>,
                        'lat': <long int>,
                        'long': <long int>,
                        'line_order': <int>,
                        'broken': <boolean>,
                        'moved': <boolean>}
        """

        args = request.args
        result = sess.query(Trap)
        if 'line_id' in args: result = result.filter_by(line_id=args['line_id'])
        if 'trap_id' in args: result = result.filter_by(id=args['trap_id'])
        # consider moving this formatting to a method in Trap
        return {'result': [trap.getDict() for trap in result.all()]}

    def put(self):
        """
        /trap PUT request will write or edit trap objects into the database

        Input:
        - JSONArray: [trap...]
        - Trap Object: {'id': <int>, (Optional: if given, overrides set in database. If excluded, creates new line)
                        'line_id': <int>,
                        'rebait_time': <long int>,
                        'lat': <long int>,
                        'long': <long int>,
                        'line_order': <int>
                        'broken': <boolean> (Optional on editing set, don't include if creating new trap)
                        'moved': <boolean> (Optional on editing set, don't include if creating new trap)}
        """

        json_data = request.get_json()

        #authenticate(line_id, args['password']) # TODO: Return error if can't validate

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
        return {'result': [trap.getDict() for trap in traps]}

    def delete(self):
        pass


class CatchInterface(Resource):
    def get(self):
        """
        /catch GET request will return catches in JSON format back to the user

        Filters (Optional):
        - line_id=<int> : filters results by line id given by relationship query to a trap
        - trap_id=<int> : filters results by trap id given

        Returned:
        - JSONObject: {'result': [catch...]}
        - Catch Object: {'id': <int>,
                        'trap_id: <int>,
                        'animal_id': <int>,
                        'time': <long int>}
        """
        args = request.args
        result = sess.query(Catch)
        if 'line_id' in args: result = result.join(Trap.id).filter(Trap.line_id == args['line_id']) # TODO: Test relationship query
        if 'trap_id' in args: result = result.filter_by(id=args['trap_id'])

        return {'result': [catch.getDict() for catch in result.all()]}

    def put(self):
        """
        /catch PUT request will write or edit catch objects into the database

        Input:
        - JSONArray: [catch...]
        - Catch Object: {'id': <int>, (Optional: if given, overrides set in database. If excluded, creates new line)
                        'trap_id': <int>,
                        'animal_id': <int>,
                        'time': <long int> (Ignored when overriding set in database)}
        """
        json_data = request.get_json()

        #authenticate(line_id, args['password']) # TODO: Return error if can't validate

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

        return {'result': [catch.getDict() for catch in catches]}

    def delete(self):
        pass


def authenticate(line_id, password):
    """
    Authenticate an inputed password by comparing the line_id hashed password against given password

    Arguments:
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
