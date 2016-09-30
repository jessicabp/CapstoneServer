from flask import Flask
from flask import request, url_for, redirect
from flask_restful import Resource, Api
import hashlib
import os
import binascii
import logging
import web_classes as wb
import orm
from orm import Line, Trap, Catch, Animal

app = Flask(__name__)
api = Api(app)

sess = orm.get_session()


class LineInterface(Resource):
    def get(self):
        """
        /line GET request will return lines in JSON format back to the user

        Args:
            - line_id=<int> : filters results by id given (Optional)
            - name=<string> : filters results by searching for string input as substring (Optional)

        Returns:
            - JSONObject: {"result": [Line...]}
            - Line Object: {"id": <int>,
                            "name": <string>}

        Example:
            - /line             ->  [{"id":1, "name":"Foo"}, {"id":2, "name":"Bar"}]
            - /line?line_id=1   ->  [{"id":1, "name":"Foo"}]
            - /line?name=Ba     ->  [{"id":2, "name":"Bar"}]
        """
        args = request.args
        result = sess.query(Line)
        if 'line_id' in args: result = result.filter_by(id=args['line_id'])
        if 'name' in args: result = result.filter(Line.name.like("%{}%".format(args['name'])))
        return {'result': [line.getDict() for line in result.all()]}, 200

    def put(self):
        """
        /line PUT request will write or edit line objects into the database

        Content-type: application/json
        Payload:
            - JSONArray: [Line...]
            - Line Object: {"id": <int>, (Optional: if given, overrides set in database. If excluded, creates new line)
                            "name": <string>,
                            "password": <string>}

        Example payload:
            [{"id":1, "name":"Foo", "password":"1234"}]
        """

        json_data = request.get_json()

        # Error checking for processing data
        if not isinstance(json_data, list):
            return {"message": "non iterable datatype passed with lines"}, 400

        lines = []
        try:
            for line_data in json_data:
                if "id" in line_data: # ID passed, only edit name of new line
                    line = sess.query(Line).filter_by(id=line_data['id']).first()
                    if not authenticate(line_data['id'], line_data['password']):
                        return {"message": "could not validate password"}, 403

                    line.name = line_data['name']

                else: # ID isn't passed, create new line
                    # Create salt and hash password
                    salt = os.urandom(40)
                    hashed = hashlib.pbkdf2_hmac('sha1', str.encode(line_data['password']), salt, 100000)

                    # Create line and store in database
                    line = Line(line_data['name'], binascii.hexlify(hashed).decode("utf-8"), binascii.hexlify(salt))
                    lines.append(line)
                    sess.add(line)
        except:
            sess.rollback()
            return {"message": "could not enter line into database (Missing key/failure to write)"}, 400

        sess.commit()
        return {'result': [line.getDict() for line in lines]}, 201

    def delete(self):
        """
        /line DELETE request will delete only 1 line in the database

        Content-type: application/json
        Payload:
            - JSONObject: {"lineId": <int>,
                           "password": <string>}

        """
        json_data = request.get_json()

        if authenticate(json_data['lineId'], json_data['password']):
            sess.query(Line).filter_by(id = json_data['lineId']).delete()
            sess.commit()
            return None, 201
        else:
            return {"message": "line doesn't exist"}, 401


class TrapInterface(Resource):
    def get(self):
        """
        /trap GET request will return traps in JSON format back to the user

        Args (Optional):
        - line_id=<int> : filters results by line id given
        - trap_id=<int> : filters results by trap id given

        Returns:
        - JSONObject: {'result': [Trap...]}
        - Trap Object: {'id': <int>,
                        'rebaitTime': <long int>,
                        'latitude': <float>,
                        'longitude': <float>,
                        'lineId': <int>,
                        'number': <int>,
                        'side': <int>,
                        'broken': <boolean>,
                        'moved': <boolean>}

        Example:
            - /trap?line_id=1   ->  [{TrapObject}, {TrapObject}, {TrapObject}]
            - /trap?trap_id=1   ->  [{TrapObject}]
        """

        args = request.args
        result = sess.query(Trap)
        if 'line_id' in args: result = result.filter_by(line_id=args['line_id'])
        if 'trap_id' in args: result = result.filter_by(id=args['trap_id'])
        return {'result': [trap.getDict() for trap in result.all()]}, 200

    def put(self):
        """
        /trap PUT request will write or edit trap objects into the database

        Content-type: application/json
        Payload:
            - JSONObject: {"lineId": <int>
                           "password": <string>,
                           "traps": [Trap...]}
            - Trap Object: {'id': <int>, (Optional: if given, overrides set in database. If excluded, creates new line)
                            'rebaitTime': <long int>,
                            'latitude': <float>,
                            'longitude': <float>,
                            'lineId': <int>,
                            'number': <int>,
                            'side': <int>,
                            'broken': <boolean>, (Optional on editing set, don't include if creating new trap)
                            'moved': <boolean> (Optional on editing set, don't include if creating new trap)}

        Example payload:
            {"line_id":1, "password":"1234", "traps":[{TrapObject}, {TrapObject}, {TrapObject}]}
        """

        json_data = request.get_json()

        if not authenticate(json_data['lineId'], json_data['password']):
            return {"message": "could not validate password"}, 403

        if not isinstance(json_data['traps'], list):
            return {"message": "non iterable datatype passed with traps"}, 400

        traps = []
        try:
            for trap_data in json_data['traps']:
                if "id" in trap_data: # ID passed, edit parameters of trap
                    trap = sess.query(Trap).filter_by(id=trap_data['id']).first()

                    # Edit values apart of trap
                    trap.lat = trap_data['latitude']
                    trap.long = trap_data['longitude']
                    if "number" in trap_data:
                        trap.line_order = trap_data['number']
                    if "side" in trap_data:
                        trap.path_side = trap_data['side']
                    if "broken" in trap_data:
                        trap.broken = trap_data['broken']
                    if "moved" in trap_data:
                        trap.moved = trap_data['moved']

                else:  # Trap doesn't exist, create a new trap
                    trap = Trap(trap_data['rebaitTime'],
                                trap_data['latitude'],
                                trap_data['longitude'],
                                trap_data['lineId'],
                                trap_data['number'],
                                trap_data['side'],
                                )
                    traps.append(trap)
                    sess.add(trap)
        except:
            sess.rollback()
            return {"message": "could not enter trap into database (Missing key/failure to write)"}, 400

        sess.commit()
        return {'result': [trap.getDict() for trap in traps]}, 201

    def delete(self):
        """
        /trap DELETE request will delete multiple traps in the database belonging to one line

        Content-type: application/json
        Payload:
            - JSONObject: {"lineId": <int>,
                           "password": <string>,
                           "traps": [<int>...]}

        """
        json_data = request.get_json()
        if authenticate(json_data['lineId'], json_data['password']):
            # Make sure they all belong to the same line
            traps = sess.query(Trap).filter(Trap.id.in_(json_data['traps'])).all()
            for trap in traps:
                if trap.line_id != json_data['lineId']:
                    return {"message": "trap belongs to different line"}, 400

            # Delete traps
            sess.query(Trap).filter(Trap.id.in_(json_data['traps'])).delete(synchronize_session='fetch')
            sess.commit()
            return None, 201
        else:
            return {"message": "could not validate user"}, 401


class CatchInterface(Resource):
    def get(self):
        """
        /catch GET request will return catches in JSON format back to the user

        Args:
        - line_id=<int> : filters results by line id given by relationship query to a trap (Optional)
        - trap_id=<int> : filters results by trap id given (Optional)

        Returned:
            JSONObject: {'result': [catch...]}
            Catch Object: {'id': <int>,
                           'trap_id: <int>,
                           'animal_id': <int>,
                           'time': <long int>}
        """
        args = request.args
        result = sess.query(Catch)
        if 'line_id' in args: result = result.join(Trap).filter(Trap.line_id == args['line_id'])
        if 'trap_id' in args: result = result.filter_by(trap_id=args['trap_id'])

        return {'result': [catch.getDict() for catch in result.all()]}, 200

    def put(self):
        """
        /catch PUT request will write or edit catch objects into the database

        Content-type: application/json
        Payload:
            JSONObject:   {"lineId": <int>
                           "password": <string>,
                           "catches": [Catch...]}
            Catch Object: {'id': <int>, (Optional: if given, overrides set in database. If excluded, creates new line)
                           'trapId': <int>,
                           'animalId': <int>,
                           'time': <long int> (Ignored when overriding set in database)}
        """
        json_data = request.get_json()

        if not authenticate(json_data['lineId'], json_data['password']):
            return {"message": "could not validate password"}, 403

        if not isinstance(json_data["catches"], list):
            return {"message": "non iterable datatype passed with catches"}, 400

        catches = []
        try:
            for catch_data in json_data["catches"]:
                if "id" in catch_data:
                    catch = sess.query(Catch).filter_by(id=catch_data['id']).first()

                    #Edit values in catch
                    catch.trap_id = catch_data['trapId']
                    catch.animal_id = catch_data['animalId']

                else: # ID not given, create new catch
                    catch = Catch(catch_data['trapId'],
                                  catch_data['animalId'],
                                  catch_data['time'])
                    catches.append(catch)
                    sess.add(catch)
        except:
            sess.rollback()
            return {"message": "could not enter catch into database (Missing key/failure to write)"}, 400

        sess.commit()
        return {'result': [catch.getDict() for catch in catches]}, 201


class AnimalInterface(Resource):
    def get(self):
        """
        /animal GET request will return animals in JSON format back to the user

        Args:
        - name=<string> : filters results by searching for string input as substring (Optional)

        Returned:
            JSONObject: {"result": [animal...]}
            Animal Object: {"id": <int>,
                           "name": <string>}
        """
        args = request.args
        result = sess.query(Animal)
        if 'name' in args: result = result.filter(Animal.name.like("%{}%".format(args['name'])))

        return {'result': [animal.getDict() for animal in result.all()]}, 200

    def put(self):
        """
        /api/animal PUT request will write or edit catch objects into the database

        Content-type: application/json
        Payload:
            JSONObject:   {"lineId": <int>
                           "password": <string>,
                           "animals": [<string>...]}
        """
        json_data = request.get_json()

        try:
            if not authenticate(json_data['lineId'], json_data['password']):
                return {"message": "could not validate password"}, 403

            if not isinstance(json_data["animals"], list):
                return {"message": "non iterable datatype passed with catches"}, 400

            animals = []

            for animal_name in json_data["animals"]:
                    animal = Animal(animal_name)
                    animals.append(animal)
                    sess.add(animal)
        except:
            sess.rollback()
            return {"message": "could not enter catch into database (Missing key/failure to write)"}, 400

        sess.commit()
        return {'result': [animal.getDict() for animal in animals]}, 201


def authenticate(line_id, password):
    """
    Authenticate an inputed password by comparing the line_id hashed password against given password

    Args:
        line_id -- Line id to compared hashed password stored in database to
        password -- Password to compared hashed password against
    """
    line = sess.query(Line).filter_by(id=line_id).first()
    if line is None:
        return False

    hash_compare = hashlib.pbkdf2_hmac('sha1', str.encode(password), binascii.unhexlify(line.salt), 100000)

    return binascii.hexlify(hash_compare).decode("utf-8") == line.password_hashed

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


@app.route("/catches/<int:number>", methods=["GET"])
def catches(number):
    return wb.catches(number)


@app.route("/edit/<int:number>", methods=["GET"])
def edit(number):
    return wb.edit(number)


if __name__ == '__main__':
    app.run(debug=False)