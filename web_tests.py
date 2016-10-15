import unittest

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

site_url = "http://127.0.0.1:5000/"
delay = 30


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
        self.driver.get(site_url)
        self.assertIn("Trap Tracker", self.driver.title)
        header = self.driver.find_element_by_tag_name("h1")
        self.assertEqual("Trap Tracker", header.text)

    def test_invalid_line_search(self):
        self.driver.get(site_url)
        elems = self.driver.find_elements_by_tag_name("input")
        self.assertEqual(len(elems), 1)
        elem = elems.pop()
        elem.clear()
        elem.send_keys("ZA^ASD*^&&^")  # Which person will use this as their line name?
        self.assertIn("No matching records found", self.driver.page_source)


    # Function to help test using the navigation bar
    def nav_using_nav_bar(self, location_to):
        previous_page = self.driver.find_element_by_tag_name("html")
        navElem = self.driver.find_element_by_tag_name("nav")
        navElem.find_element_by_link_text(location_to).click()

        WebDriverWait(self.driver, delay).until(EC.staleness_of(previous_page))

    def test_nav_bar_to_home(self):
        self.driver.get(site_url + "create")
        self.nav_using_nav_bar("Home")
        self.assertEqual(site_url, self.driver.current_url)

    def test_nav_bar_to_create_line(self):
        self.driver.get(site_url)
        self.nav_using_nav_bar("Create Line")
        self.assertEqual(site_url + "create", self.driver.current_url)

    def test_nav_bar_to_about(self):
        self.driver.get(site_url)
        self.nav_using_nav_bar("About")
        self.assertEqual(site_url + "about", self.driver.current_url)


    # Function to help get from home page to login screens (Any random one)
    def to_login_page(self, link):
        self.driver.get(site_url)
        WebDriverWait(self.driver, delay).until(
            EC.presence_of_element_located((By.ID, "lines"))
        )

        previous_page = self.driver.find_element_by_tag_name("html")
        table = self.driver.find_element_by_id('lines')
        table.find_elements_by_link_text(link).pop().click()

        WebDriverWait(self.driver, delay).until(EC.staleness_of(previous_page))

        return self.driver.find_element_by_tag_name("h1")

    def test_login_page_by_settings(self):
        header = self.to_login_page("Edit")
        self.assertEqual("Login", header.text)

    def test_login_page_by_catches(self):
        header = self.to_login_page("Catches")
        self.assertEqual("Login", header.text)

    def test_login_page_by_settings(self):
        header = self.to_login_page("Settings")
        self.assertEqual("Login", header.text)


    # Function to accessing past the login screens
    def past_login_screen(self, link):
        self.driver.get(site_url)
        WebDriverWait(self.driver, delay).until(
            EC.presence_of_element_located((By.ID, "lines"))
        )

        previous_page = self.driver.find_element_by_tag_name("html")
        web_line = self.driver.find_element_by_id('lines').find_element_by_class_name("even")
        web_line.find_elements_by_link_text(link).pop().click()

        WebDriverWait(self.driver, delay).until(EC.staleness_of(previous_page))

        previous_page = self.driver.find_element_by_tag_name("html")
        form = self.driver.find_element_by_name("password")
        form.send_keys("!s0meth@ng")
        form.send_keys(Keys.RETURN)

        WebDriverWait(self.driver, delay).until(EC.staleness_of(previous_page))

    @unittest.skipIf(site_url == "https://traptracker.pythonanywhere.com/", "Skip test due to non-fixed data")
    def test_access_traps(self):
        self.past_login_screen("Edit")
        self.assertEqual("Traps in Manatawu Gorge", self.driver.find_element_by_tag_name("h1").text)

    @unittest.skipIf(site_url == "https://traptracker.pythonanywhere.com/", "Skip test due to non-fixed data")
    def test_access_catches(self):
        self.past_login_screen("Catches")
        self.assertEqual("Catches for Manatawu Gorge", self.driver.find_element_by_tag_name("h1").text)

    @unittest.skipIf(site_url == "https://traptracker.pythonanywhere.com/", "Skip test due to non-fixed data")
    def test_access_settings(self):
        self.past_login_screen("Settings")
        self.assertEqual("Settings", self.driver.find_element_by_tag_name("h1").text)


class ChromeTesting(unittest.TestCase):
    def setUp(self):
        capabilities = DesiredCapabilities.CHROME

        self.driver = WebDriver(command_executor='http://127.0.0.1:4444/wd/hub',
                                desired_capabilities=capabilities)

    def tearDown(self):
        self.driver.close()

    def test_get_home_page(self):
        self.driver.get(site_url)
        self.assertIn("Trap Tracker", self.driver.title)
        header = self.driver.find_element_by_tag_name("h1")
        self.assertEqual("Trap Tracker", header.text)

    def test_invalid_line_search(self):
        self.driver.get(site_url)
        elems = self.driver.find_elements_by_tag_name("input")
        self.assertEqual(len(elems), 1)
        elem = elems.pop()
        elem.clear()
        elem.send_keys("ZA^ASD*^&&^")  # Which person will use this as their line name?
        self.assertIn("No matching records found", self.driver.page_source)


    # Function to help test using the navigation bar
    def nav_using_nav_bar(self, location_to):
        previous_page = self.driver.find_element_by_tag_name("html")
        navElem = self.driver.find_element_by_tag_name("nav")
        navElem.find_element_by_link_text(location_to).click()

        WebDriverWait(self.driver, delay).until(EC.staleness_of(previous_page))

    def test_nav_bar_to_home(self):
        self.driver.get(site_url + "create")
        self.nav_using_nav_bar("Home")
        self.assertEqual(site_url, self.driver.current_url)

    def test_nav_bar_to_create_line(self):
        self.driver.get(site_url)
        self.nav_using_nav_bar("Create Line")
        self.assertEqual(site_url + "create", self.driver.current_url)

    def test_nav_bar_to_about(self):
        self.driver.get(site_url)
        self.nav_using_nav_bar("About")
        self.assertEqual(site_url + "about", self.driver.current_url)


    # Function to help get from home page to login screens (Any random one)
    def to_login_page(self, link):
        self.driver.get(site_url)
        WebDriverWait(self.driver, delay).until(
            EC.presence_of_element_located((By.ID, "lines"))
        )

        previous_page = self.driver.find_element_by_tag_name("html")
        table = self.driver.find_element_by_id('lines')
        table.find_elements_by_link_text(link).pop().click()

        WebDriverWait(self.driver, delay).until(EC.staleness_of(previous_page))

        return self.driver.find_element_by_tag_name("h1")

    def test_login_page_by_settings(self):
        header = self.to_login_page("Edit")
        self.assertEqual("Login", header.text)

    def test_login_page_by_catches(self):
        header = self.to_login_page("Catches")
        self.assertEqual("Login", header.text)

    def test_login_page_by_settings(self):
        header = self.to_login_page("Settings")
        self.assertEqual("Login", header.text)


    # Function to accessing past the login screens
    def past_login_screen(self, link):
        self.driver.get(site_url)
        WebDriverWait(self.driver, delay).until(
            EC.presence_of_element_located((By.ID, "lines"))
        )

        previous_page = self.driver.find_element_by_tag_name("html")
        web_line = self.driver.find_element_by_id('lines').find_element_by_class_name("even")
        web_line.find_elements_by_link_text(link).pop().click()

        WebDriverWait(self.driver, delay).until(EC.staleness_of(previous_page))

        previous_page = self.driver.find_element_by_tag_name("html")
        form = self.driver.find_element_by_name("password")
        form.send_keys("!s0meth@ng")
        form.send_keys(Keys.RETURN)

        WebDriverWait(self.driver, delay).until(EC.staleness_of(previous_page))

    @unittest.skipIf(site_url == "https://traptracker.pythonanywhere.com/", "Skip test due to non-fixed data")
    def test_access_traps(self):
        self.past_login_screen("Edit")
        self.assertEqual("Traps in Manatawu Gorge", self.driver.find_element_by_tag_name("h1").text)

    @unittest.skipIf(site_url == "https://traptracker.pythonanywhere.com/", "Skip test due to non-fixed data")
    def test_access_catches(self):
        self.past_login_screen("Catches")
        self.assertEqual("Catches for Manatawu Gorge", self.driver.find_element_by_tag_name("h1").text)

    @unittest.skipIf(site_url == "https://traptracker.pythonanywhere.com/", "Skip test due to non-fixed data")
    def test_access_settings(self):
        self.past_login_screen("Settings")
        self.assertEqual("Settings", self.driver.find_element_by_tag_name("h1").text)


if __name__ == "__main__":
    unittest.main()