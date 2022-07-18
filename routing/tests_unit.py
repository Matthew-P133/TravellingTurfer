from django.test import TestCase
from django.urls import reverse
from routing.models import Zone


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

