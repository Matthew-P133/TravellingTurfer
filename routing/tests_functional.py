from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import geckodriver_autoinstaller

# install geckodriver if not installed and add it to path
geckodriver_autoinstaller.install()

class PageLoadTest(StaticLiveServerTestCase):

    def setUp(self):
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(options=options)

    def tearDown(self):
        self.browser.quit()

    def testPageLoads(self):
        self.browser.get(self.live_server_url)
        self.assertIn('TravellingTurfer', self.browser.title)