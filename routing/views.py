from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.urls import reverse
import requests
import json
from routing.models import Waypoints, Zone, Distance, Route, createRoute, generateDistanceMatrix
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

    # get zones from database if not too large an area
    if (abs(northEastLat - southWestLat) < 0.25 and abs(northEastLong - southWestLong) < 1.0):
        zones = Zone.objects.filter(latitude__gte=southWestLat).filter(longitude__gte=southWestLong).filter(latitude__lte=northEastLat).filter(longitude__lte=northEastLong).values()
        return JsonResponse(list(zones), safe=False)
    else:
        return JsonResponse([{'error':'Area requested is too large'}], safe=False)


def optimise(request):

    if request.method == 'POST':

        # check request data
        try:
            zones = json.loads(request.body)
        except:
            return HttpResponseBadRequest()

        if not all(isinstance(zone, int) for zone in zones):
            return HttpResponseBadRequest()

        if len(zones) > 100:
            return HttpResponseBadRequest()

        # populate distance matrix from database
        distanceMatrix = generateDistanceMatrix(zones)
    
        # main algorithm
        start = time.time()
        if len(zones) <= 7:
            print("Using bruteforce algorithm...")
            shortestRoute = bruteForce.optimise(zones, distanceMatrix)
        elif len(zones) <= 40:
            print("Using Christofide's algorithm...")
            shortestRoute = christofides.optimise(zones, distanceMatrix)
        else:
            print("Using nearest neighbour algorithm...")
            shortestRoute = nearestNeighbour.optimise(zones, distanceMatrix)

        print(f"{routing_utils.distance(shortestRoute, distanceMatrix)} km route found in {time.time() - start} seconds")

        # extra heuristics
        if len(zones) > 7:

            print('Optimising with 2-opt...')
            start = time.time()
            shortestRoute = twoOpt.optimise(shortestRoute, distanceMatrix)
            print(f"Optimised to {routing_utils.distance(shortestRoute, distanceMatrix)} km route in {time.time() - start} seconds")

            if len(zones) < 75:

                print('Optimising with 3-opt...')
                start = time.time()
                shortestRoute = threeOpt.optimise(shortestRoute, distanceMatrix)
                print(f"Optimised to {routing_utils.distance(shortestRoute, distanceMatrix)} km route in {time.time() - start} seconds")

        # save route to the database
        route = createRoute(shortestRoute)

        # returns route id of newly created route; javascript redirects user to route page
        return HttpResponse(route.id)
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])


# generates geoJSON for display of a given route
def generate(request):
    if request.method == 'POST':


        # check request data
        try:
            id = json.loads(request.body)
        except:
            return HttpResponseBadRequest()

        if not len(id) == 1 or not isinstance(id[0], int):
            return HttpResponseBadRequest()

        try:
            geoJSON = Route.objects.get(id=id[0]).getGeoJSON()
            return JsonResponse(geoJSON)
        except:
            return HttpResponseBadRequest()

    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

