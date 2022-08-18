
import django
from django.conf import settings
import os
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TravellingTurfer.settings')
django.setup()

from routing.models import Zone
import json


def populate():

    # query turf api for all zones
    x = requests.get("http://api.turfgame.com/v4/zones/all")
    zone_dict = json.loads(x.content)

    new_zones = []
    count = 0

    # add any new zones to the database
    for zone in zone_dict:

        # limit to zones in scotland
        if zone['region']['id'] == 200:
       
            if not Zone.objects.filter(id=zone['id']):
            
                new_zone = Zone(id=zone['id'], name=zone['name'], latitude=zone['latitude'], longitude=zone['longitude'], 
                                date_created=zone['dateCreated'], takeovers=zone['totalTakeovers'], points_per_hour=zone['pointsPerHour'], 
                                takeover_points=zone['takeoverPoints'])          
                new_zones.append(new_zone)

                # display progress in the terminal
                count += 1
                if (count % 100 == 0):
                    print(f"Added {count} new zones...", end='\r')
            
    Zone.objects.bulk_create(new_zones)
    print(f"Successfully added {count} new zones")

    
if (__name__ == '__main__'):
    print("Starting zone population script...")
    populate()
    print('Databases successfully populated')