import datetime
from re import L
from django.db import models
from django.utils.timezone import now
from geopy import distance


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
    
def createRoute(zones):

    route = Route()
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

    # calculate distance when a new pair is added to the database
    def save(self, *args, **kwargs):
        
        start = self.zone_a
        end = self.zone_b
        self.distance = straightLineDistance(start, end)
        super().save(*args, **kwargs)
        

# helper method to calculate straight line distance between two zones
def straightLineDistance(start, end):

    startCoord = (start.latitude, start.longitude)
    endCoord = (end.latitude, end.longitude)
    straightLineDistance = distance.distance(startCoord, endCoord).km
    return straightLineDistance





