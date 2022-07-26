from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
import requests
import json
from routing.models import Waypoints, Zone, Distance, Route, createRoute
import routing.bruteForce as bruteForce
import routing.nearestNeighbour as nearestNeighbour
import routing.christofides as christofides
import routing.twoOpt as twoOpt
import routing.threeOpt as threeOpt
import routing.routing_utils as routing_utils
import time



# redirect / to map page
def index(request):
    return redirect(reverse('routing:map'))


# main map page
def map(request):

    return render(request, 'routing/map.html')

# page for already created route
def route(request, id):

    context_dict = {"id":id}

    return render(request, 'routing/route.html', context=context_dict)


def zones(request):

    coords = json.loads(request.body)

    northEastLat = coords['northEastLat']
    northEastLong = coords['northEastLong']
    southWestLat = coords['southWestLat']
    southWestLong = coords['southWestLong']

    # get zones from Turf API

    #data = [{'northEast' : {'latitude':northEastLat, 'longitude':northEastLong}, 'southWest' : {'latitude':southWestLat, 'longitude':southWestLong}}]
    #response = requests.post("http://api.turfgame.com/v4/zones", headers = {"Content-Type": "application/json"}, data=json.dumps(data))
    #zones_json = response.content

    # get zones from locally cached zones if not too large an area
    if (abs(northEastLat - southWestLat) < 0.25 and abs(northEastLong - southWestLong) < 1.0):
        zones = Zone.objects.filter(latitude__gte=southWestLat).filter(longitude__gte=southWestLong).filter(latitude__lte=northEastLat).filter(longitude__lte=northEastLong).values()
        return JsonResponse(list(zones), safe=False)
    else:
        return JsonResponse([{'error':'Area requested is too large'}], safe=False)


def optimise(request):

    zones = json.loads(request.body)

    # populate distance matrix from database
    distanceMatrix = {zone:{} for zone in zones}

    for zoneA in zones:
        for zoneB in zones:
            start = Zone.objects.get(id=zoneA)
            end = Zone.objects.get(id=zoneB)
            distance = Distance.objects.get_or_create(zone_a=start, zone_b=end)[0].distance
            distanceMatrix[zoneA].update({zoneB: distance})

    # main algorithm
    start = time.time()
    if len(zones) <= 7:
        print("Using bruteforce algorithm...")
        shortestRoute = bruteForce.optimise(zones, distanceMatrix)
    elif len(zones) <= 55:
        print("Using Christofide's algorithm...")
        shortestRoute = christofides.optimise(zones, distanceMatrix)
    else:
        print("Using nearest neighbour algorithm...")
        shortestRoute = nearestNeighbour.optimise(zones, distanceMatrix)

    print(f"{routing_utils.distance(shortestRoute, distanceMatrix)} km route found in {time.time() - start} seconds")

    # extra heuristics

    print('Optimising with 2-opt...')
    start = time.time()
    shortestRoute = twoOpt.optimise(shortestRoute, distanceMatrix)
    print(f"Optimised to {routing_utils.distance(shortestRoute, distanceMatrix)} km route in {time.time() - start} seconds")

    print('Optimising with 3-opt...')
    start = time.time()
    shortestRoute = threeOpt.optimise(shortestRoute, distanceMatrix)
    print(f"Optimised to {routing_utils.distance(shortestRoute, distanceMatrix)} km route in {time.time() - start} seconds")

    # save it to the database
    route = createRoute(shortestRoute)

    # returns route id of newly created route; javascript redirects user route page
    return HttpResponse(route.id)


# generates geoJSON for display of a given route
def generate(request):
    id = json.loads(request.body)['id']
    route = Route.objects.get(id=id)
    geoJSON = route.getGeoJSON()

    return JsonResponse(geoJSON)


