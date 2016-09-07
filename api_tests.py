import unittest
import flask_app
import json
from datetime import datetime
from orm import Line, Trap, Catch


testLine = Line("Manawatu", "1234", "Nothing here")
testTrap = Trap(datetime.now(), -40.310124, 175.777104, 1, 1, 1)
testCatch = Catch(1, 1, datetime.now())


class TestLineInterface(unittest.TestCase):
    def setUp(self):
        # TODO: Set up temporary database to do testing on
        flask_app.app.config["TESTING"] = True
        self.app = flask_app.app.test_client()

    def tearDown(self):
        # TODO: Remove fixed id
        flask_app.sess.query(Line).filter(Line.id == 1).delete()
        flask_app.sess.commit()

    def testGet(self):
        entiresBefore = len(flask_app.sess.query(Line).all())
        flask_app.sess.add(testLine)
        flask_app.sess.commit()
        responseJSON = json.loads(self.app.get("/line").data.decode("utf-8"))["result"]

        self.assertEqual(entiresBefore+1, len(responseJSON), "Line table update not returned by /line GET")
        self.assertEqual(testLine.name, responseJSON[0]["name"], "Line.name data modified returned by /line GET")

    def testPut(self):
        entiresBefore = len(flask_app.sess.query(Line).all())
        jsonData = json.dumps([{"name": testLine.name, "password": testLine.password_hashed}])
        response = self.app.put("/line", data=jsonData, content_type="application/json")
        self.assertEqual(entiresBefore+1, len(flask_app.sess.query(Line).all()))


class TestTrapInterface(unittest.TestCase):
    def setUp(self):
        # TODO: Set up temporary database to do testing on
        flask_app.app.config["TESTING"] = True
        self.app = flask_app.app.test_client()

    def tearDown(self):
        # TODO: Remove fixed id
        flask_app.sess.query(Line).filter(Line.id == 1).delete()
        flask_app.sess.commit()

    def testGet(self):
        entiresBefore = len(flask_app.sess.query(Trap).all())
        flask_app.sess.add(testTrap)
        flask_app.sess.commit()
        responseJSON = json.loads(self.app.get("/trap").data.decode("utf-8"))["result"]

        self.assertEqual(entiresBefore+1, len(responseJSON), "Trap table update not returned by /trap GET")
        #self.assertEqual(testTrap.rebait_time) TODO: convert datetime to JSON
        self.assertEqual(testTrap.lat, responseJSON[0]["lat"], "Trap.name data modified returned by /trap GET")
        self.assertEqual(testTrap.long, responseJSON[0]["long"], "Trap.long data modified returned by /trap GET")
        self.assertEqual(testTrap.line_order, responseJSON[0]["line_order"], "Trap.line_order data modified returned by /trap GET")
        self.assertEqual(testTrap.path_side, responseJSON[0]["path_side"], "Trap.path_side data modified returned by /trap GET")
        self.assertEqual(testTrap.broken, responseJSON[0]["broken"], "Trap.broken data modified returned by /trap GET")
        self.assertEqual(testTrap.moved, responseJSON[0]["moved"], "Trap.moved data modified returned by /trap GET")


    def testPut(self):
        entiresBefore = len(flask_app.sess.query(Trap).all())
        jsonData = json.dumps([{"rebait_time": {"year": testTrap.rebait_time.year,
                                                "month": testTrap.rebait_time.month,
                                                "day": testTrap.rebait_time.day,
                                                "hour": testTrap.rebait_time.hour,
                                                "minute": testTrap.rebait_time.minute,
                                                "second": testTrap.rebait_time.second,
                                                "microsecond": testTrap.rebait_time.microsecond},
                                "lat": testTrap.lat,
                                "long": testTrap.long,
                                "line_id": testTrap.line_id,
                                "line_order": testTrap.line_order,
                                "path_side": testTrap.path_side}])
        response = self.app.put("/trap", data=jsonData, content_type="application/json")
        self.assertEqual(entiresBefore+1, len(flask_app.sess.query(Line).all()))


class TestCatchInterface(unittest.TestCase):
    def setUp(self):
        # TODO: Set up temporary database to do testing on
        flask_app.app.config["TESTING"] = True
        self.app = flask_app.app.test_client()

    def tearDown(self):
        # TODO: Remove fixed id
        flask_app.sess.query(Line).filter(Line.id == 1).delete()
        flask_app.sess.commit()

    def testGet(self):
        entiresBefore = len(flask_app.sess.query(Catch).all())
        flask_app.sess.add(testCatch)
        flask_app.sess.commit()
        responseJSON = json.loads(self.app.get("/catch").data.decode("utf-8"))["result"]

        self.assertEqual(entiresBefore+1, len(responseJSON), "Trap table update not returned by /catch GET")
        self.assertEqual(testCatch.trap_id, responseJSON[0]["trap_id"], "Catch.name data modified returned by /catch GET")
        self.assertEqual(testCatch.animal_id, responseJSON[0]["animal_id"], "Catch.name data modified returned by /catch GET")
        #self.assertEqual(testCatch.time, responseJSON[0]["time"], "Catch.name data modified returned by /trap GET") TODO: Convert datetime to JSON

    def testPut(self):
        entiresBefore = len(flask_app.sess.query(Trap).all())
        jsonData = json.dumps([{"trap_id": testCatch.trap_id,
                                "animal_id": testCatch.animal_id,
                                "time": {"year": testTrap.rebait_time.year,
                                         "month": testTrap.rebait_time.month,
                                         "day": testTrap.rebait_time.day,
                                         "hour": testTrap.rebait_time.hour,
                                         "minute": testTrap.rebait_time.minute,
                                         "second": testTrap.rebait_time.second,
                                         "microsecond": testTrap.rebait_time.microsecond}}])
        response = self.app.put("/catch", data=jsonData, content_type="application/json")
        self.assertEqual(entiresBefore+1, len(flask_app.sess.query(Line).all()))


if __name__ == "__main__":
    unittest.main()