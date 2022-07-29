from django.test import TestCase
from django.urls import reverse
from routing.models import Zone, Waypoints
import random
import json

class MapViewTest(TestCase):

    def test_url_exists(self):
        response = self.client.get("/map/")
        self.assertEqual(response.status_code, 200)

    def test_index_redirects_to_map(self):
        response = self.client.get("/")
        self.assertRedirects(response, reverse('routing:map'))

    def test_url_accessible_by_name(self):
        response = self.client.get(reverse("routing:map"))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get(reverse("routing:map"))
        self.assertTemplateUsed(response, 'routing/map.html')


class RoutingViewTest(TestCase):

    def test_url_exists(self):
        response = self.client.get("/route437/")
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get('/route437/')
        self.assertTemplateUsed(response, 'routing/route.html')

    def test_URL_suffix_passed_to_template(self):
        response = self.client.get('/route437/')
        self.assertEqual(response.context['id'], 437)
 

class ZoneAPITest(TestCase):

    def setUp(self):
        zone = Zone.objects.create(id=21520, name='Geijers', latitude=59.333521, longitude=18.012366, 
                            date_created="2013-09-05T06:53:34Z", takeovers=5646, points_per_hour=5, 
                            takeover_points=125)

    def test_get_zones(self):
        payload = {
            'northEastLat': 59.35297109149536,
            'northEastLong': 18.185291290283207,
            'southWestLat': 59.300428078876216,
            'southWestLong': 17.968311309814457
        }
        response = self.client.post('/zones/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Geijers')

    def test_request_large_area(self):
        payload = {
            'northEastLat': 59.35,
            'northEastLong': 18.19,
            'southWestLat': 59.05,
            'southWestLong': 17.05
        }
        response = self.client.post('/zones/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Geijers')
        self.assertContains(response, "Area requested is too large")

class OptimiseTest(TestCase):

    # populate test database with test zones and distances
    fixtures = ['testZones.json', 'testDistances.json']

    def test_request_method(self):
        response = self.client.get('/optimise/')
        self.assertEquals(response.status_code, 405)

    def test_malformed_requests(self):
        # empty payload
        payload = ''
        response = self.client.post('/optimise/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 400)
        # payload contains non-integers
        payload = 'random'
        response = self.client.post('/optimise/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 400)

    # test too large route request
    def test_reject_oversize_request(self):
        zones = []
        for i in range(1000):
            zones.append(random.randint(1, 100))
        payload = json.dumps(zones)
        response = self.client.post('/optimise/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 400)

    def test_brute_force_algorithm(self):
        # make request and test 200 status code
        payload = json.dumps([16006, 15378, 16975, 173258])
        response = self.client.post('/optimise/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 200)
        # get waypoints of route from database and check in expected order
        id = json.loads(response.content)
        waypoints = Waypoints.objects.filter(route_id=id)
        self.assertEqual(len(waypoints), len(json.loads(payload))+1)
        correctOrder = [16006, 15378, 173258, 16975, 16006]
        for i, waypoint in enumerate(waypoints):
            self.assertEqual(waypoint.position, i)
            self.assertEqual(waypoint.zone_id, correctOrder[i])

    def test_christofides_algorithm(self):
        # make request and test 200 status code
        payload = json.dumps([15378, 15379, 15380, 15396, 15446, 15447, 15448, 15454, 15457, 15458, 15459, 15460, 15713, 15714, 16064, 16065, 16066, 16067, 16068, 16069, 16073, 16075, 173254, 173255, 173256, 173257, 476494, 476496, 476525])
        response = self.client.post('/optimise/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 200)
        # get waypoints of route from database and check in expected order
        id = json.loads(response.content)
        waypoints = Waypoints.objects.filter(route_id=id)
        self.assertEqual(len(waypoints), len(json.loads(payload))+1)
        correctOrder = [16065, 15447, 173254, 15396, 15448, 16064, 16066, 16068, 16069, 16067, 15457, 15378, 15713, 476525, 15459, 15458, 173257, 15380, 173256, 173255, 15379, 476496, 15714, 476494, 15460, 16075, 16073, 15454, 15446, 16065]
        for i, waypoint in enumerate(waypoints):
            self.assertEqual(waypoint.position, i)
            self.assertEqual(waypoint.zone_id, correctOrder[i])

    def test_nearest_neighbour_algorithm(self):
        # make request and test 200 status code
        payload = json.dumps([15380, 15396, 15399, 15446, 15447, 15448, 15451, 15452, 15453, 16004, 16005, 173254, 173255, 173256, 173259, 323827, 346792, 516844, 15378, 15379, 15455, 15457, 16064, 16065, 16066, 16067, 16068, 16069, 411367, 476496, 496582, 15458, 15459, 15713, 15714, 328273, 476494, 476495, 476525, 15460, 411351, 411353, 411354])
        response = self.client.post('/optimise/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 200)
        # get waypoints of route from database and check in expected order
        id = json.loads(response.content)
        waypoints = Waypoints.objects.filter(route_id=id)
        self.assertEqual(len(waypoints), len(json.loads(payload))+1)
        correctOrder = [15380, 173256, 15446, 173254, 15448, 15447, 173255, 15379, 15378, 16065, 16064, 16066, 16068, 16069, 15455, 411367, 496582, 16067, 15457, 476496, 15713, 15458, 15459, 476525, 15460, 476494, 476495, 411354, 411351, 411353, 328273, 15714, 15396, 15453, 15399, 323827, 15452, 346792, 16004, 15451, 16005, 173259, 516844, 15380]
        for i, waypoint in enumerate(waypoints):
            self.assertEqual(waypoint.position, i)
            self.assertEqual(waypoint.zone_id, correctOrder[i])


# tests the /generate/ endpoint
class GenerateTest(TestCase):

    # populate test database with test zones, distances and routes
    fixtures = ['testZones.json', 'testDistances.json', 'testRoutes.json', 'testWaypoints.json']

    def test_request_method(self):
        response = self.client.get('/generate/')
        self.assertEquals(response.status_code, 405)

    def test_malformed_requests(self):
        # empty payload
        payload = ''
        response = self.client.post('/generate/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 400)
        # payload contains non-integers
        payload = 'random'
        response = self.client.post('/generate/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 400)

    # test returns valid geoJSON for existing route
    def test_valid_request(self):
        payload = json.dumps([215])
        response = self.client.post('/generate/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 200)
        geoJSON = json.loads(response.content)
        self.assertTrue(len(geoJSON) == 2)
        self.assertTrue('type' in geoJSON)
        self.assertTrue('coordinates' in geoJSON)
        self.assertTrue(geoJSON['coordinates'] is not None)

    # test return for non-exisitng route
    def test_invalid_request(self):
        payload = json.dumps([100])
        response = self.client.post('/generate/', payload, content_type='application/json')
        self.assertEquals(response.status_code, 400)
