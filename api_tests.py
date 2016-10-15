import unittest
from traptracker import app
import traptracker.test_data as test_data
import json
import traptracker.orm as orm
from traptracker.orm import Line, Trap, Catch, Animal
from traptracker.auth import authenticate, AUTH_NONE, AUTH_CATCH, AUTH_LINE


testLine = Line("Massey Uni Line", "1234", "5678", "", 1, 2, 3)
testTrap = Trap(-40.310124, 175.777104, 1, 5, 1)
testCatch = Catch(1, 1, 1473431831)
testAnimal1 = Animal("Possom")
testAnimal2 = Animal("Ferret")

lineUrl = "/api/line"
trapUrl = "/api/trap"
catchUrl = "/api/catch"
animalUrl = "/api/animal"
authUrl = "/api/checkauth"
baseUrl = "https://localhost"


class TestLineInterface(unittest.TestCase):
    data_bits = "1000"

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        test_data.wipeDatabase(self.data_bits)
        test_data.pushData(self.data_bits)

    def tearDown(self):
        test_data.wipeDatabase(self.data_bits)

    def testGet_Base(self):
        responseJSON = json.loads(self.app.get(lineUrl, base_url=baseUrl).data.decode("utf-8"))["result"]

        self.assertEqual(len(responseJSON), 2, "/line not returning correct amount")

    def testGet_LineQuery(self):
        responseJSON = json.loads(self.app.get(lineUrl + "?line_id=1", base_url=baseUrl).data.decode("utf-8"))["result"]

        self.assertEqual(len(responseJSON), 1, "/line?line_id not returning correct amount")
        self.assertEqual(responseJSON[0]['name'], "Manatawu Gorge", "/line?line_id table not returning correct name")

    def testGet_NameQeury(self):
        responseJSON = json.loads(self.app.get(lineUrl + "?name=Kai", base_url=baseUrl).data.decode("utf-8"))["result"]

        self.assertEqual(len(responseJSON), 1, "/line?name not returning correct amount")
        self.assertEqual(responseJSON[0]['id'], 2, "/line?name incorrect id returned")

    def testPut(self):
        sess = orm.get_session()
        entiresBefore = len(sess.query(Line).all())
        jsonData = json.dumps([{"name": testLine.name, "password": testLine.password_hashed,
                                "admin_password": testLine.password_hashed,
                                "animal1": 1, "animal2": 2, "animal3": 3}])

        self.app.put(lineUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        # Test increase of one + data integrity of password
        self.assertEqual(entiresBefore+1, len(sess.query(Line).all()), "/line did not add testLine")
        line = sess.query(Line).filter_by(id=3).first()
        self.assertEqual(line.name, testLine.name, "/line name not stored correctly")
        self.assertTrue(authenticate(line.id, testLine.password_hashed)>=AUTH_LINE, "/line password could not validate")
        sess.close()

    def testDelete(self):
        sess = orm.get_session()
        entiresBefore = len(sess.query(Line).all())
        jsonData = json.dumps({"lineId": 1, "password": "!s0meth@ng"})

        self.app.delete(lineUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(entiresBefore-1, len(sess.query(Line).all()), "/line DELETE did not delete line")
        sess.close()


class TestTrapInterface(unittest.TestCase):
    data_bits = "1100"

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        test_data.wipeDatabase(self.data_bits)
        test_data.pushData(self.data_bits)

    def tearDown(self):
        test_data.wipeDatabase(self.data_bits)

    def testGet_Base(self):
        responseJSON = json.loads(self.app.get(trapUrl, base_url=baseUrl).data.decode("utf-8"))["message"]

        self.assertEqual(responseJSON, "no argument given", "Incorrect response returned")

    def testGet_LineQuery(self):
        responseJSON = json.loads(self.app.get(trapUrl+ "?line_id=1", base_url=baseUrl).data.decode("utf-8"))["result"]

        self.assertEqual(len(responseJSON), 4, "/trap?line_id not returning correct amount")

    def testGet_TrapQuery(self):
        responseJSON = json.loads(self.app.get(trapUrl + "?trap_id=5", base_url=baseUrl).data.decode("utf-8"))["result"]

        self.assertEqual(len(responseJSON), 1, "/trap?trap_id not returning correct amount")
        self.assertEqual(responseJSON[0]['latitude'], -40.312435, "/trap?trap_id returned incorrect lat")
        self.assertEqual(responseJSON[0]['longitude'], 175.780965, "/trap?trap_id returned incorrect long")
        self.assertEqual(responseJSON[0]['number'], 4, "/trap?trap_id returned incorrect line_order")

    def testPut(self):
        sess = orm.get_session()
        entiresBefore = len(sess.query(Trap).all())
        jsonData = json.dumps({"lineId": 1,
                               "password": "!s0meth@ng",
                                "traps": [
                                {"latitude": testTrap.lat,
                                "longitude": testTrap.long,
                                "lineId": testTrap.line_id,
                                "number": testTrap.line_order,
                                "side": testTrap.path_side}]
                               })

        response = self.app.put(trapUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        # Test increase of one + data integrity of all data passed
        self.assertEqual(entiresBefore+1, len(sess.query(Trap).all()), "/trap did not add testTrap")
        trap = sess.query(Trap).filter_by(id=7).first()
        self.assertEqual(trap.lat, testTrap.lat, "/trap lat not stored correctly")
        self.assertEqual(trap.long, testTrap.long, "/trap long not stored correctly")
        self.assertEqual(trap.line_id, testTrap.line_id, "/trap line_id not stored correctly")
        self.assertEqual(trap.line_order, testTrap.line_order, "/trap line_order not stored correctly")
        self.assertEqual(trap.path_side, testTrap.path_side, "/trap path_side not stored correctly")
        sess.close()

    def testPut_editTraps(self):
        sess = orm.get_session()
        entiresBefore = len(sess.query(Trap).all())
        jsonData = json.dumps({"lineId": 1,
                               "password": "!s0meth@ng",
                               "traps": [
                               {"id": 1,
                                "latitude": 42.22,
                                "longitude": 4410.3312,
                                "number": 42,
                                "side": testTrap.path_side,
                                "broken": True,
                                "moved": True}]
                               })

        response = self.app.put(trapUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        # Test increase of one + data integrity of all data passed
        self.assertEqual(entiresBefore, len(sess.query(Trap).all()), "/trap did not add testTrap")
        trap = sess.query(Trap).filter_by(id=1).first()
        self.assertEqual(trap.lat, 42.22, "/trap lat not edited")
        self.assertEqual(trap.long, 4410.3312, "/trap long not edited")
        self.assertEqual(trap.line_order, 42, "/trap line_order not edited")
        self.assertEqual(trap.broken, True, "/trap broken not edited")
        self.assertEqual(trap.moved, True, "/trap moved not edited")
        sess.close()

    def testDelete(self):
        sess = orm.get_session()
        entiresBefore = len(sess.query(Trap).all())
        jsonData = json.dumps({"lineId": 1,
                           "password": "!s0meth@ng",
                           "traps": [1,4]})
        self.app.delete(trapUrl, data=jsonData, content_type="application/json", base_url=baseUrl)
        self.assertEqual(entiresBefore-2, len(sess.query(Trap).all()), "/trap DELETE did not delete traps")
        sess.close()


class TestCatchInterface(unittest.TestCase):
    data_bits = "1110"

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        test_data.wipeDatabase(self.data_bits)
        test_data.pushData(self.data_bits)

    def tearDown(self):
        test_data.wipeDatabase(self.data_bits)

    def testGet_Base(self):
        responseJSON = json.loads(self.app.get(catchUrl, base_url=baseUrl).data.decode("utf-8"))["message"]

        self.assertEqual(responseJSON, "no argument given", "Incorrect response returned")

    def testGet_LineQuery(self):
        responseJSON = json.loads(self.app.get(catchUrl + "?line_id=2", base_url=baseUrl).data.decode("utf-8"))["result"]

        self.assertEqual(len(responseJSON), 5, "/catch?line_id not returning correct amount")

    def testGet_TrapQuery(self):
        responseJSON = json.loads(self.app.get(catchUrl + "?trap_id=6", base_url=baseUrl).data.decode("utf-8"))["result"]

        self.assertEqual(len(responseJSON), 3, "/catch?trap_id not returning correct amount")

    def testPut(self):
        sess = orm.get_session()
        entiresBefore = len(sess.query(Catch).all())
        jsonData = json.dumps({"lineId": 1,
                                "password": "password",
                                "catches": [{"trapId": testCatch.trap_id,
                                            "animalId": testCatch.animal_id,
                                            "time": testCatch.time}]
                                })

        response = self.app.put(catchUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        # Test increase of one + data integrity of all data passed
        self.assertEqual(entiresBefore+1, len(sess.query(Catch).all()))
        catch = sess.query(Catch).filter_by(id=8).first()
        self.assertEqual(catch.trap_id, testCatch.trap_id, "/catch trap_id not stored correctly")
        self.assertEqual(catch.animal_id, testCatch.animal_id, "/catch animal_id not stored correctly")
        self.assertEqual(catch.time, testCatch.time, "/catch time not stored correctly")
        sess.close()

    def testPut_NonListFailure(self):
        jsonData = json.dumps({"lineId": 1,
                                "password": "password",
                                "catches": {"trapId": testCatch.trap_id,
                                            "animalId": testCatch.animal_id,
                                            "time": testCatch.time}
                                })

        response = self.app.put(catchUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 400, "Wrong error code returned with non list for traps")
        self.assertIn("non iterable datatype passed with catches", response.data.decode("utf-8"), "Wrong message given")

    def testPut_CantAuthenticateFailure(self):
        jsonData = json.dumps({"lineId": 1, "password":"incorrect"})  # No password or traps given

        response = self.app.put(catchUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 403, "Wrong error code returned with failure to authenticate")
        self.assertIn("could not validate password", response.data.decode("utf-8"), "Wrong message given")

    def testPut_MissingKeyFailure(self):
        jsonData = json.dumps({"lineId": 1, "password":"password", "catches":[{"time": testCatch.time}]})

        response = self.app.put(catchUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 400, "Wrong error code returned with missing key")
        self.assertIn("could not enter catch into database", response.data.decode("utf-8"), "Wrong message given")

    def testDelete(self):
        sess = orm.get_session()
        entiresBefore = len(sess.query(Catch).all())
        jsonData = json.dumps({"lineId": 1,
                               "password": "!s0meth@ng",
                               "catches": [1,4]})

        self.app.delete(catchUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(entiresBefore-2, len(sess.query(Catch).all()), "/catch DELETE did not delete catch")
        sess.close()


class TestAnimalInterface(unittest.TestCase):
    data_bits = "1001"

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        test_data.wipeDatabase(self.data_bits)
        test_data.pushData(self.data_bits)

    def tearDown(self):
        test_data.wipeDatabase(self.data_bits)

    def testGet_Base(self):
        responseJSON = json.loads(self.app.get(animalUrl, base_url=baseUrl).data.decode("utf-8"))["result"]

        self.assertEqual(len(responseJSON), 4, "/animal not returning correct amount with base query")

    def testGet_LineQuery(self):
        responseJSON = json.loads(self.app.get(animalUrl + "?name=C", base_url=baseUrl).data.decode("utf-8"))["result"]

        self.assertEqual(len(responseJSON), 1, "/animal?line_id not returning correct amount")

    def testPut(self):
        sess = orm.get_session()
        entiresBefore = len(sess.query(Animal).all())
        jsonData = json.dumps({"lineId": 1,
                                "password": "password",
                                "animals": [testAnimal1.name, testAnimal2.name]
                                })

        response = self.app.put(animalUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        # Test increase of one + data integrity of all data passed
        self.assertEqual(entiresBefore+2, len(sess.query(Animal).all()))
        animal = sess.query(Animal).filter_by(id=5).first()
        self.assertEqual(animal.name, testAnimal1.name, "/animal time not stored correctly")
        sess.close()

    def testPut_NonListFailure(self):
        jsonData = json.dumps({"lineId": 1,
                                "password": "password",
                                "animals": testAnimal1.name
                                })

        response = self.app.put(animalUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 400, "Wrong error code returned with non list for traps")
        self.assertIn("non iterable datatype passed with catches", response.data.decode("utf-8"), "Wrong message given")

    def testPut_CantAuthenticateFailure(self):
        jsonData = json.dumps({"lineId": 1,
                                "password": "incorrect",
                                "animals": [testAnimal1.name, testAnimal2.name]
                                })

        response = self.app.put(animalUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 403, "Wrong error code returned with failure to authenticate")
        self.assertIn("could not validate password", response.data.decode("utf-8"), "Wrong message given")

    def testPut_MissingKeyFailure(self):
        jsonData = json.dumps({"lineId": 1,
                                "animals": [testAnimal1.name, testAnimal2.name]
                                })

        response = self.app.put(animalUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 400, "Wrong error code returned with missing key")
        self.assertIn("could not enter catch into database", response.data.decode("utf-8"), "Wrong message given")


class TestAuthInterface(unittest.TestCase):
    data_bits = "1000"

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        test_data.wipeDatabase(self.data_bits)
        test_data.pushData(self.data_bits)

    def tearDown(self):
        test_data.wipeDatabase(self.data_bits)

    def testGet_userAuth(self):
        response = self.app.get(authUrl + "?line_id=1&password=password", base_url=baseUrl)

        jsonResponse = json.loads(response.data.decode("utf-8"))

        self.assertEqual(response.mimetype, "application/json", "/checkauth not returning correct mimetype")
        self.assertEqual(jsonResponse["result"], 1, "/checkauth not returning correct level")

    def testGet_adminAuth(self):
        response = self.app.get(authUrl + "?line_id=1&password=!s0meth@ng", base_url=baseUrl)

        jsonResponse = json.loads(response.data.decode("utf-8"))

        self.assertEqual(response.mimetype, "application/json", "/checkauth not returning correct mimetype")
        self.assertEqual(jsonResponse["result"], 2, "/checkauth not returning correct level")

    def testGet_argsFailure(self):
        response = self.app.get(authUrl + "?line_id=1", base_url=baseUrl)

        self.assertEqual(response.mimetype, "application/json", "/checkauth not returning correct mimetype")
        self.assertEqual(response.status_code, 400, "Wrong error code returned with missing key")


classes = [TestLineInterface, TestTrapInterface, TestCatchInterface, TestAnimalInterface, TestAuthInterface]

if __name__ == "__main__":
    unittest.main()
