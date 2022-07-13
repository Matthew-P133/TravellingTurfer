from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import json
from routing.models import Zone



# main map page
def map(request):

    return render(request, 'routing/map.html')

# page for already created route
def route(request, id):

    context_dict = {"id":id}

    return render(request, 'routing/route.html', context=context_dict)


def zones(request):

    northEastLat = request.POST['northEastLat']
    northEastLong = request.POST['northEastLong']
    southWestLat = request.POST['southWestLat']
    southWestLong = request.POST['southWestLong']

    # get zones from Turf API

    #data = [{'northEast' : {'latitude':northEastLat, 'longitude':northEastLong}, 'southWest' : {'latitude':southWestLat, 'longitude':southWestLong}}]
    #response = requests.post("http://api.turfgame.com/v4/zones", headers = {"Content-Type": "application/json"}, data=json.dumps(data))
    #zones_json = response.content

    # get zones from locally cached zones

    zones = Zone.objects.filter(latitude__gte=southWestLat).filter(longitude__gte=southWestLong).filter(latitude__lte=northEastLat).filter(longitude__lte=northEastLong).values()
    
    return JsonResponse(list(zones), safe=False)
    