import unittest
import flask_app
import json
from orm import Line, Trap, Catch


testLine = Line("Manawatu", "1234")
testTrap = Trap(1472376505, -40.310124, 175.777104, 1, 1, 1)
testCatch = Catch(1, 1, 1472379999)


class TestLineInterface(unittest.TestCase):
    def setUp(self):
        # TODO: Set up temporary database to do testing on
        flask_app.app.config["TESTING"] = True
        self.app = flask_app.app.test_client()

    def tearDown(self):
        # TODO: Remove fixed id
        flask_app.sess.query(Line).filter(Line.id == 2).delete()

    def testGet(self):
        entiresBefore = len(flask_app.sess.query(Line).all())
        flask_app.sess.add(testLine)
        flask_app.sess.commit()
        responseJSON = json.loads(self.app.get("/line").data.decode("utf-8"))
        self.assertEqual(entiresBefore+1, len(responseJSON["result"]))
        # TODO: Compare dict response with test object


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

    def testGet(self):
        entiresBefore = len(flask_app.sess.query(Trap).all())
        flask_app.sess.add(testTrap)
        flask_app.sess.commit()
        responseJSON = json.loads(self.app.get("/trap").data.decode("utf-8"))
        self.assertEqual(entiresBefore+1, len(responseJSON["result"]))
        # TODO: Compare dict response with test object


    def testPut(self):
        entiresBefore = len(flask_app.sess.query(Trap).all())
        jsonData = json.dumps([{"rebait_time": testTrap.rebait_time,
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

    def testGet(self):
        entiresBefore = len(flask_app.sess.query(Catch).all())
        flask_app.sess.add(testCatch)
        flask_app.sess.commit()
        responseJSON = json.loads(self.app.get("/catch").data.decode("utf-8"))
        self.assertEqual(entiresBefore+1, len(responseJSON["result"]))
        # TODO: Compare dict response with test object


    def testPut(self):
        entiresBefore = len(flask_app.sess.query(Trap).all())
        jsonData = json.dumps([{"trap_id": testCatch.trap_id,
                                "animal_id": testCatch.animal_id,
                                "time": testCatch.time}])
        response = self.app.put("/catch", data=jsonData, content_type="application/json")
        self.assertEqual(entiresBefore+1, len(flask_app.sess.query(Line).all()))


if __name__ == "__main__":
    unittest.main()