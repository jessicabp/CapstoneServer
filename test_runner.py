import unittest
import api_tests
import api_test_failures

runner = unittest.TextTestRunner()
classes = api_tests.classes + api_test_failures.classes

for test in classes:
    runner.run(unittest.makeSuite(test))

