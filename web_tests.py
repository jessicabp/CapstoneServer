import unittest

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys


class FirefoxTesting(unittest.TestCase):
    def setUp(self):
        capabilities = DesiredCapabilities.FIREFOX
        capabilities['platform'] = "WIN10"
        capabilities['marionette'] = True
        capabilities['binary'] = "C:\Program Files (x86)\Firefox Developer Edition"

        self.driver = WebDriver(command_executor='http://127.0.0.1:4444/wd/hub',
                                desired_capabilities=capabilities)

    def tearDown(self):
        self.driver.close()

    def test_get_home_page(self):
        self.driver.get("https://traptracker.pythonanywhere.com/")
        self.assertIn("Trap Tracker", self.driver.title)
        self.assertIn("Trap Tracker", self.driver.page_source)

    def test_invalid_line_search(self):
        self.driver.get("https://traptracker.pythonanywhere.com/")
        elems = self.driver.find_elements_by_tag_name("input")
        self.assertEqual(len(elems), 1)
        elem = elems.pop()
        elem.clear()
        elem.send_keys("ZA^ASD*^&&^")  # Which person will use this as their line name?
        self.assertIn("No matching records found", self.driver.page_source)


class ChromeTesting(unittest.TestCase):
    def setUp(self):
        capabilities = DesiredCapabilities.CHROME

        self.driver = WebDriver(command_executor='http://127.0.0.1:4444/wd/hub',
                                desired_capabilities=capabilities)

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()