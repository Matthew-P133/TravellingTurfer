import datetime
from django.db import models

class Zone(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    date_created = models.DateTimeField(default=datetime.datetime.now())
    takeovers = models.IntegerField(default=0)
    points_per_hour = models.IntegerField(default=0)
    takeover_points = models.IntegerField(default=0)



