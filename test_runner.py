import unittest
import api_tests
import api_failure_tests

runner = unittest.TextTestRunner()
classes = api_tests.classes + api_failure_tests.classes

for test in classes:
    runner.run(unittest.makeSuite(test))

