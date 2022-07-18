from datetime import datetime
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import geckodriver_autoinstaller
from urllib.parse import urljoin
import time

# install geckodriver if not installed and add it to path
geckodriver_autoinstaller.install()

TIMEOUT = 5

# smart wait for testing anything asynchronous
def wait_helper(fn):
    start = time.time()
    while True:
        try:
            return fn()
        except(AssertionError, Exception) as e:
            if (time.time() - start > TIMEOUT):
                raise e
            time.sleep(0.5)


class FunctionalTestsDB(StaticLiveServerTestCase):

    fixtures = ['fixtures.json']

    def setUp(self):
        options = Options()
        #options.headless = True
        self.browser = webdriver.Firefox(options=options)

    def tearDown(self):
        self.browser.quit()

    
    def testMapPage(self):
        self.browser.get(urljoin(self.live_server_url, 'map/'))
        self.assertIn('Map', self.browser.title)

        # check that map loads
        wait_helper(lambda: self.assertIsNot("", self.browser.execute_script('return document.getElementById(\'map\').innerHtml;')))

        # zoom map and check that zones displayed

        self.browser.find_element('css selector', '.leaflet-control-zoom-in').click()
        wait_helper(lambda: self.assertGreater(self.browser.execute_script('zoneCount = 0; markerGroup.eachLayer(zone => zoneCount++); return zoneCount;'), 0))

        # click on zones and check that stats are updated

        markers = self.browser.find_elements('css selector', '.leaflet-interactive')
        for i in range(3):
            markers[i].click()

        wait_helper(lambda: self.assertEqual(self.browser.execute_script('zoneCount = 0; selectedMarkerGroup.eachLayer(zone => zoneCount++); return zoneCount;'), 3))
        self.assertIsNot("", self.browser.execute_script('return document.getElementById(\'selectedZoneCount\').innerHtml;'))
        self.assertIsNot("", self.browser.execute_script('return document.getElementById(\'selectedZoneTakeoverPoints\').innerHtml;'))
        self.assertIsNot("", self.browser.execute_script('return document.getElementById(\'selectedZonePointsPerHour\').innerHtml;'))


class FunctionalTestsNoDB(StaticLiveServerTestCase):

    def setUp(self):
        options = Options()
        #options.headless = True
        self.browser = webdriver.Firefox(options=options)

    def tearDown(self):
        self.browser.quit()

    def testIndexPage(self):
        self.browser.get(self.live_server_url)
        self.assertIn('TravellingTurfer', self.browser.title)

    def testRoutePage(self):
        self.browser.get(urljoin(self.live_server_url, 'route437'))
        self.assertIn('Route', self.browser.title)
        self.assertIn('437', self.browser.page_source)

