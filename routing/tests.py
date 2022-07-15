from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

import geckodriver_autoinstaller

# install geckodriver if not installed and add it to path
geckodriver_autoinstaller.install()

class PageLoadTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def testPageLoads(self):
        self.browser.get(self.live_server_url)
        self.assertIn('TravellingTurfer', self.browser.title)

