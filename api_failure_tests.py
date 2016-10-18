import unittest
from traptracker import app
import traptracker.test_data as test_data
import json
from traptracker.orm import Line, Trap, Catch, Animal


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


class TestTrapInterfaceFailures(unittest.TestCase):
    data_bits = "1100"

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        test_data.wipeDatabase(self.data_bits)
        test_data.pushData(self.data_bits)

    def tearDown(self):
        test_data.wipeDatabase(self.data_bits)

    def testPut_NonListFailure(self):
        jsonData = json.dumps({"lineId": 1,
                               "password": "password",
                               "traps":
                               {"latitude": testTrap.lat,
                                "longitude": testTrap.long,
                                "lineId": testTrap.line_id,
                                "number": testTrap.line_order,
                                "side": testTrap.path_side}
                               })

        response = self.app.put(trapUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 400, "Wrong error code returned with non list for traps")
        self.assertIn("non iterable datatype passed with traps", response.data.decode("utf-8"), "Wrong message given")

    def testPut_CantAuthenticateFailure(self):
        jsonData = json.dumps({"lineId": 1, "password": "incorrect"})  # No password or traps given

        response = self.app.put(trapUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 403, "Wrong error code returned with failure to authenticate")
        self.assertIn("could not validate password", response.data.decode("utf-8"), "Wrong message given")

    def testPut_MissingKeyFailure(self):
        jsonData = json.dumps({"lineId": 1, "password": "!s0meth@ng", "traps": [{"lat": testTrap.lat}]})

        response = self.app.put(trapUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 400, "Wrong error code returned with missing key")
        self.assertIn("could not enter trap into database", response.data.decode("utf-8"), "Wrong message given")

    def testPut_LowAuthFailure(self):
        jsonData = json.dumps({"lineId": 1,
                               "password": "password",
                               "traps":
                               [{"latitude": testTrap.lat,
                                 "longitude": testTrap.long,
                                 "lineId": testTrap.line_id,
                                 "number": testTrap.line_order,
                                 "side": testTrap.path_side}]
                               })

        response = self.app.put(trapUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 403, "Wrong error code returned for low auth level")
        self.assertIn("could not validate admin password", response.data.decode("utf-8"), "Wrong message given")

    def testDelete_LowAuthFailure(self):
        jsonData = json.dumps({"lineId": 1,
                               "password": "password",
                               "traps": [1, 4]})

        response = self.app.delete(trapUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 401, "Wrong error code returned with low auth level")
        self.assertIn("could not validate user", response.data.decode("utf-8"), "Wrong message given")

    def testDelete_DifferentLineFailure(self):
        jsonData = json.dumps({"lineId": 1,
                               "password": "!s0meth@ng",
                               "traps": [1, 2, 3, 4, 5, 6]})

        response = self.app.delete(trapUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 400, "Wrong error code returned with traps not on same line")
        self.assertIn("trap belongs to different line", response.data.decode("utf-8"), "Wrong message given")


class TestCatchInterfaceFailures(unittest.TestCase):
    data_bits = "1110"

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        test_data.wipeDatabase(self.data_bits)
        test_data.pushData(self.data_bits)

    def tearDown(self):
        test_data.wipeDatabase(self.data_bits)

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

    def testDelete_LowAuthFailure(self):
        jsonData = json.dumps({"lineId": 1,
                               "password": "password",
                               "catches": [1, 4]})

        response = self.app.delete(catchUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 401, "Wrong error code returned with low auth level")
        self.assertIn("could not validate user", response.data.decode("utf-8"), "Wrong message given")

    def testDelete_DifferentLineFailure(self):
        jsonData = json.dumps({"lineId": 1,
                               "password": "!s0meth@ng",
                               "catches": [1, 2, 3, 4, 5, 6]})

        response = self.app.delete(catchUrl, data=jsonData, content_type="application/json", base_url=baseUrl)

        self.assertEqual(response.status_code, 400, "Wrong error code returned with catches not on same line")
        self.assertIn("catch belongs to different line", response.data.decode("utf-8"), "Wrong message given")


class TestAnimalInterfaceFailures(unittest.TestCase):
    data_bits = "1001"

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        test_data.wipeDatabase(self.data_bits)
        test_data.pushData(self.data_bits)

    def tearDown(self):
        test_data.wipeDatabase(self.data_bits)

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


class TestAuthInterfaceFailures(unittest.TestCase):
    data_bits = "1000"

    def setUp(self):
        app.config["TESTING"] = True
        self.app = app.test_client()
        test_data.wipeDatabase(self.data_bits)
        test_data.pushData(self.data_bits)

    def tearDown(self):
        test_data.wipeDatabase(self.data_bits)

    def requestAuth(self, args):
        response = self.app.get(authUrl + args, base_url=baseUrl)

        self.assertEqual(response.mimetype, "application/json", "/checkauth not returning correct mimetype")
        self.assertEqual(response.status_code, 400, "Wrong error code returned with missing key")
        self.assertIn("needs line_id and password url parameters", response.data.decode("utf-8"), "Wrong message given")

    def testGet_bothArgsFailure(self):
        self.requestAuth("?random=args")

    def testGet_MissingPasswordArgFailure(self):
        self.requestAuth("?line_id=1")

    def testGet_MissingPasswordArgFailure(self):
        self.requestAuth("?password=password")


classes = [TestTrapInterfaceFailures, TestCatchInterfaceFailures,
           TestAnimalInterfaceFailures, TestAuthInterfaceFailures]

if __name__ == "__main__":
    unittest.main()
