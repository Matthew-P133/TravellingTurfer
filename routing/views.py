from django.shortcuts import render
from django.http import HttpResponse
import requests
import json



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

    data = [{'northEast' : {'latitude':northEastLat, 'longitude':northEastLong}, 'southWest' : {'latitude':southWestLat, 'longitude':southWestLong}}]
    
    x = requests.post("http://api.turfgame.com/v4/zones", headers = {"Content-Type": "application/json"}, data=json.dumps(data))

    return HttpResponse(x.content)
    