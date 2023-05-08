import datetime
from re import L
from django.db import models
from django.utils.timezone import now
from geopy import distance
import json
import requests
import dotenv
import os

dotenv.load_dotenv()


# stores information relating to Turf zones
class Zone(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    date_created = models.DateTimeField(default=now)
    takeovers = models.IntegerField(default=0)
    points_per_hour = models.IntegerField(default=0)
    takeover_points = models.IntegerField(default=0)

# models a route made up of several zones
class Route(models.Model):

    # primary key is default auto incrementing 'id' field
    date_created = models.DateTimeField(default=now)
    
    def getDistance(self):

        waypoints = Waypoints.objects.filter(route=self)

        distance = 0
        for i, zone in enumerate(waypoints):
            if i != len(waypoints)-1:
                start = waypoints[i].zone
                end = waypoints[i+1].zone

                distance += Distance.objects.get(zone_a=start, zone_b=end).distance

        return distance

    def getGeoJSON(self):

        waypoints = Waypoints.objects.filter(route=self).order_by('position')

        coordinates = []

        for i, zone in enumerate(waypoints):
            if i != len(waypoints)-1:
                start = waypoints[i].zone
                end = waypoints[i+1].zone
                segment = Distance.objects.get(zone_a=start, zone_b=end)
                segmentCoordinates = json.loads(segment.geoJSON)['coordinates']
                for coordinate in segmentCoordinates:
                    coordinates.append(coordinate)
                
        geoJSON = {
            'type': 'LineString',
            'coordinates': coordinates
        }

        return geoJSON

def createRoute(route, zones):

    waypoints = []

    for position, zone in enumerate(zones):
            
            waypoint = Waypoints(route=route, zone=Zone.objects.get(id=zone), position=position)
            waypoints.append(waypoint)

    route.save()
    for waypoint in waypoints:
        waypoint.save()

    return route

# stores which zones are in which routes and their order
class Waypoints(models.Model):

    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    position = models.IntegerField(default=0)

# cache of distances between pairs of zones (for generating distance matrices)
class Distance(models.Model):

    zone_a = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='start')
    zone_b = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='end')
    distance = models.FloatField(default=0.0)
    date_obtained = models.DateTimeField(default=now)
    geoJSON = models.CharField(max_length=10000, default='')

    # generate geoJSON for A->B and get A->B distance...
    def save(self, *args, **kwargs):
        
        start = self.zone_a
        end = self.zone_b

        if os.getenv('straight') == 'True':
            distance = straightLineDistance(start, end)
            coordinates = [[zone.longitude, zone.latitude] for zone in [self.zone_a, self.zone_b]]
        
        else:
            if start.id == end.id:
                distance = 0
                coordinates = []
            else:
                routeData = route(start, end)
                distance = routeData['distance']
                coordinates = routeData['coordinates']

        geoJSON = {
            'type': 'LineString',
            'coordinates': coordinates
        }     

        self.geoJSON = json.dumps(geoJSON)
        self.distance = distance

        super().save(*args, **kwargs)

class Job(models.Model):

    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    message = models.CharField(max_length=200, default='loading...')
    status = models.BooleanField(default=False)
    base_distance = models.FloatField(default=0.0)
    shortest = models.FloatField(default=0.0)
    method = models.CharField(max_length=20, default='')
    two_opt = models.BooleanField(default=False)
    two_opt_improvement = models.FloatField(default=0.0)
    three_opt = models.BooleanField(default=False)
    three_opt_improvement = models.FloatField(default=0.0)

    # performance measurements
    distance_matrix_generation_ms=models.FloatField(default=-1)
    base_algorithm_ms=models.FloatField(default=-1)
    two_opt_ms=models.FloatField(default=-1)
    three_opt_ms=models.FloatField(default=-1)

        
# helper method to calculate straight line distance between two zones
def straightLineDistance(start, end):

    startCoord = (start.latitude, start.longitude)
    endCoord = (end.latitude, end.longitude)
    straightLineDistance = distance.distance(startCoord, endCoord).km
    return straightLineDistance

# helper method to get snap to road route
def route(start, end):

    routeData = {}

    # get A->B route from locally hosted graph hopper instance
    response = json.loads(requests.post(os.getenv('GRAPHHOPPER_ADDRESS'), 
                            data = json.dumps({"points": [[start.longitude, start.latitude], [end.longitude, end.latitude]],'points_encoded':False}), headers = {'Accept': 'application/json',
                            'Content-Type': 'application/json',}).content)

    routeData['distance'] = response['paths'][0]['distance'] / 1000
    routeData['coordinates'] = response['paths'][0]['points']['coordinates']

    return routeData

# helper method to generate distance matrix of A->B distances
def generateDistanceMatrix(zones, job):

    expectedElements = len(zones)*len(zones)

    distanceMatrix = {zone:{} for zone in zones}
    count = 0
    for zoneA in zones:
        for zoneB in zones:
            start = Zone.objects.get(id=zoneA)
            end = Zone.objects.get(id=zoneB)
            distance = Distance.objects.get_or_create(zone_a=start, zone_b=end)[0].distance
            distanceMatrix[zoneA].update({zoneB: distance})
            if count % 100 == 0:
                job.message = f"Generating distance matrix ({count} of {expectedElements})"
                job.save()
            count += 1

    return distanceMatrix

