import unittest
import flask_app
import test_data
import json
from orm import Line, Trap, Catch


testLine = Line("Massey Uni Line", "1234", "")
testTrap = Trap(1473431831, -40.310124, 175.777104, 1, 5, 1)
testCatch = Catch(1, 1, 1473431831)


class TestLineInterface(unittest.TestCase):
    def setUp(self):
        flask_app.app.config["TESTING"] = True
        self.app = flask_app.app.test_client()
        test_data.pushData("100")

    def tearDown(self):
        flask_app.sess.query(Line).delete()
        flask_app.sess.commit()

    def testGet_Base(self):
        responseJSON = json.loads(self.app.get("/line").data.decode("utf-8"))["result"]
        self.assertEqual(len(responseJSON), 2, "/line not returning correct amount")

    def testGet_LineQuery(self):
        responseJSON = json.loads(self.app.get("/line?line_id=1").data.decode("utf-8"))["result"]
        self.assertEqual(len(responseJSON), 1, "/line?line_id not returning correct amount")
        self.assertEqual(responseJSON[0]['name'], "Manatawu Gorge", "/line?line_id table not returning correct name")

    def testGet_NameQeury(self):
        responseJSON = json.loads(self.app.get("/line?name=Kai").data.decode("utf-8"))["result"]
        self.assertEqual(len(responseJSON), 1, "/line?name not returning correct amount")
        self.assertEqual(responseJSON[0]['id'], 2, "/line?name incorrect id returned")

    def testPut(self):
        entiresBefore = len(flask_app.sess.query(Line).all())
        jsonData = json.dumps([{"name": testLine.name, "password": testLine.password_hashed}])
        self.app.put("/line", data=jsonData, content_type="application/json")

        # Test increase of one + data integrity of password
        self.assertEqual(entiresBefore+1, len(flask_app.sess.query(Line).all()), "/line did not add testLine")
        line = flask_app.sess.query(Line).filter_by(id=3).first()
        self.assertEqual(line.name, testLine.name, "/line name not stored correctly")
        self.assertTrue(flask_app.authenticate(line.id, testLine.password_hashed), "/line password could not validate")

    def testPut_NonListFailure(self):
        jsonData = json.dumps({"name": testLine.name, "password": testLine.password_hashed})
        response = self.app.put("/line", data=jsonData, content_type="application/json")
        self.assertEqual(response.status_code, 400, "Wrong error code returned with non list for lines")
        self.assertIn("non iterable datatype passed", response.data.decode("utf-8"), "Wrong message given")

    def testPut_MissingKeyFailure(self):
        jsonData = json.dumps([{"name": testLine.name}])  # No password given
        response = self.app.put("/line", data=jsonData, content_type="application/json")
        self.assertEqual(response.status_code, 400, "Wrong error code returned with missing key")
        self.assertIn("could not enter line into database", response.data.decode("utf-8"), "Wrong message given")

    def testDelete(self):
        entiresBefore = len(flask_app.sess.query(Line).all())
        jsonData = json.dumps({"line_id": 1, "password": "password"})
        self.app.delete("/line", data=jsonData, content_type="application/json")
        self.assertEqual(entiresBefore-1, len(flask_app.sess.query(Line).all()), "/line DELETE did not delete line")


class TestTrapInterface(unittest.TestCase):
    def setUp(self):
        flask_app.app.config["TESTING"] = True
        self.app = flask_app.app.test_client()
        test_data.pushData("110")

    def tearDown(self):
        flask_app.sess.query(Line).delete()
        flask_app.sess.query(Trap).delete()
        flask_app.sess.commit()

    def testGet_Base(self):
        responseJSON = json.loads(self.app.get("/trap").data.decode("utf-8"))["result"]
        self.assertEqual(len(responseJSON), 6, "/trap not returning correct amount with base query")

    def testGet_LineQuery(self):
        responseJSON = json.loads(self.app.get("/trap?line_id=1").data.decode("utf-8"))["result"]
        self.assertEqual(len(responseJSON), 4, "/trap?line_id not returning correct amount")

    def testGet_TrapQuery(self):
        responseJSON = json.loads(self.app.get("/trap?trap_id=5").data.decode("utf-8"))["result"]
        self.assertEqual(len(responseJSON), 1, "/trap?trap_id not returning correct amount")
        self.assertEqual(responseJSON[0]['lat'], -40.312435, "/trap?trap_id returned incorrect lat")
        self.assertEqual(responseJSON[0]['long'], 175.780965, "/trap?trap_id returned incorrect long")
        self.assertEqual(responseJSON[0]['line_order'], 4, "/trap?trap_id returned incorrect line_order")

    def testPut(self):
        entiresBefore = len(flask_app.sess.query(Trap).all())
        jsonData = json.dumps({"line_id": 1,
                               "password": "password",
                                "traps": [
                                {"rebait_time": testTrap.rebait_time,
                                "lat": testTrap.lat,
                                "long": testTrap.long,
                                "line_id": testTrap.line_id,
                                "line_order": testTrap.line_order,
                                "path_side": testTrap.path_side}]
                               })
        response = self.app.put("/trap", data=jsonData, content_type="application/json")

        # Test increase of one + data integrity of all data passed
        self.assertEqual(entiresBefore+1, len(flask_app.sess.query(Trap).all()), "/trap did not add testTrap")
        trap = flask_app.sess.query(Trap).filter_by(id=7).first()
        self.assertEqual(trap.rebait_time, testTrap.rebait_time, "/trap rebait_time not stored correctly")
        self.assertEqual(trap.lat, testTrap.lat, "/trap lat not stored correctly")
        self.assertEqual(trap.long, testTrap.long, "/trap long not stored correctly")
        self.assertEqual(trap.line_id, testTrap.line_id, "/trap line_id not stored correctly")
        self.assertEqual(trap.line_order, testTrap.line_order, "/trap line_order not stored correctly")
        self.assertEqual(trap.path_side, testTrap.path_side, "/trap path_side not stored correctly")

    def testPut_NonListFailure(self):
        jsonData = json.dumps({"line_id": 1,
                               "password": "password",
                                "traps":
                                {"rebait_time": testTrap.rebait_time,
                                "lat": testTrap.lat,
                                "long": testTrap.long,
                                "line_id": testTrap.line_id,
                                "line_order": testTrap.line_order,
                                "path_side": testTrap.path_side}
                               })
        response = self.app.put("/trap", data=jsonData, content_type="application/json")
        self.assertEqual(response.status_code, 400, "Wrong error code returned with non list for traps")
        self.assertIn("non iterable datatype passed with traps", response.data.decode("utf-8"), "Wrong message given")

    def testPut_CantAuthenticateFailure(self):
        jsonData = json.dumps({"line_id": 1, "password":"incorrect"})  # No password or traps given
        response = self.app.put("/trap", data=jsonData, content_type="application/json")
        self.assertEqual(response.status_code, 403, "Wrong error code returned with failure to authenticate")
        self.assertIn("could not validate password", response.data.decode("utf-8"), "Wrong message given")

    def testPut_MissingKeyFailure(self):
        jsonData = json.dumps({"line_id": 1, "password":"password", "traps":[{"rebait_time": testTrap.rebait_time}]})
        response = self.app.put("/trap", data=jsonData, content_type="application/json")
        self.assertEqual(response.status_code, 400, "Wrong error code returned with missing key")
        self.assertIn("could not enter trap into database", response.data.decode("utf-8"), "Wrong message given")

    def testDelete(self):
        entiresBefore = len(flask_app.sess.query(Trap).all())
        jsonData = json.dumps({"line_id": 1,
                           "password": "password",
                           "traps": [1,4]})
        self.app.delete("/trap", data=jsonData, content_type="application/json")
        self.assertEqual(entiresBefore-2, len(flask_app.sess.query(Trap).all()), "/trap DELETE did not delete traps")


class TestCatchInterface(unittest.TestCase):
    def setUp(self):
        flask_app.app.config["TESTING"] = True
        self.app = flask_app.app.test_client()
        test_data.pushData("111")

    def tearDown(self):
        flask_app.sess.query(Line).delete()
        flask_app.sess.query(Trap).delete()
        flask_app.sess.query(Catch).delete()
        flask_app.sess.commit()

    def testGet_Base(self):
        responseJSON = json.loads(self.app.get("/catch").data.decode("utf-8"))["result"]
        self.assertEqual(len(responseJSON), 7, "/catch not returning correct amount with base query")

    def testGet_LineQuery(self):
        responseJSON = json.loads(self.app.get("/catch?line_id=2").data.decode("utf-8"))["result"]
        self.assertEqual(len(responseJSON), 5, "/trap?line_id not returning correct amount")

    def testGet_TrapQuery(self):
        responseJSON = json.loads(self.app.get("/catch?trap_id=6").data.decode("utf-8"))["result"]
        self.assertEqual(len(responseJSON), 3, "/catch?trap_id not returning correct amount")

    def testPut(self):
        entiresBefore = len(flask_app.sess.query(Catch).all())
        jsonData = json.dumps({"line_id": 1,
                                "password": "password",
                                "catches": [{"trap_id": testCatch.trap_id,
                                            "animal_id": testCatch.animal_id,
                                            "time": testCatch.time}]
                                })
        response = self.app.put("/catch", data=jsonData, content_type="application/json")

        # Test increase of one + data integrity of all data passed
        self.assertEqual(entiresBefore+1, len(flask_app.sess.query(Catch).all()))
        catch = flask_app.sess.query(Catch).filter_by(id=8).first()
        self.assertEqual(catch.trap_id, testCatch.trap_id, "/catch trap_id not stored correctly")
        self.assertEqual(catch.animal_id, testCatch.animal_id, "/catch animal_id not stored correctly")
        self.assertEqual(catch.time, testCatch.time, "/catch time not stored correctly")

    def testPut_NonListFailure(self):
        jsonData = json.dumps({"line_id": 1,
                                "password": "password",
                                "catches": {"trap_id": testCatch.trap_id,
                                            "animal_id": testCatch.animal_id,
                                            "time": testCatch.time}
                                })
        response = self.app.put("/catch", data=jsonData, content_type="application/json")
        self.assertEqual(response.status_code, 400, "Wrong error code returned with non list for traps")
        self.assertIn("non iterable datatype passed with catches", response.data.decode("utf-8"), "Wrong message given")

    def testPut_CantAuthenticateFailure(self):
        jsonData = json.dumps({"line_id": 1, "password":"incorrect"})  # No password or traps given
        response = self.app.put("/catch", data=jsonData, content_type="application/json")
        self.assertEqual(response.status_code, 403, "Wrong error code returned with failure to authenticate")
        self.assertIn("could not validate password", response.data.decode("utf-8"), "Wrong message given")

    def testPut_MissingKeyFailure(self):
        jsonData = json.dumps({"line_id": 1, "password":"password", "catches":[{"time": testCatch.time}]})
        response = self.app.put("/catch", data=jsonData, content_type="application/json")
        self.assertEqual(response.status_code, 400, "Wrong error code returned with missing key")
        self.assertIn("could not enter catch into database", response.data.decode("utf-8"), "Wrong message given")


if __name__ == "__main__":
    unittest.main()
