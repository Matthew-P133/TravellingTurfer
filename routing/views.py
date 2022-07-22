from tracemalloc import start
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
import requests
import json
from routing.models import Waypoints, Zone, Distance, Route, createRoute


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
    distanceMatrix = { zone:{} for zone in zones}

    # toggle straight line / snap to map routing
    straight = True

    for zoneA in zones:
        for zoneB in zones:
            start = Zone.objects.get(id=zoneA)
            end = Zone.objects.get(id=zoneB)
            distance = Distance.objects.get_or_create(zone_a=start, zone_b=end)[0].distance
            distanceMatrix[zoneA].update({zoneB: distance})

    # calculate shortest route
    response = bruteForceRoute(zones, distanceMatrix)

    # returns route id of newly created route; javascript redirects user route page
    return HttpResponse(response)


def bruteForceRoute(zones, distanceMatrix):

    routeLength = len(zones)

    # all possible routes
    routes = []

    # add first zone to route
    route = [zones[0],]

    # zones still to be visited
    notInRoute = [zones[i] for i in range(1,routeLength)]

    # brute force generate all routes
    findAllRoutes(route, notInRoute, routes)

    # find shortest
    shortestDistance = 0
    shortestRoute = []
    
    for route in routes:
        distance = routeDistance(route)
        if (distance < shortestDistance or shortestDistance == 0):
            shortestDistance = distance
            shortestRoute = route

    # save shortest route to database
    route = createRoute(shortestRoute)    

    return route.id
    

def routeDistance(route):

    distance = 0
    for i, zone in enumerate(route):
        if i != len(route)-1:
            start = Zone.objects.get(id=route[i])
            end = Zone.objects.get(id=route[i+1])
            distance += Distance.objects.get(zone_a=start, zone_b=end).distance

    return distance
        

def findAllRoutes(route, notInRoute, routes):

    # if all zones in route, go back to start and add route to routes
    if len(notInRoute) == 0:
        route.append(route[0])
        routes.append(route)

    # otherwise for each not in route zone add it to the route, make a new call to findAllRoutes
    else:
        for zone in notInRoute:
            newRoute = route.copy()
            newRoute.append(zone)

            newNotInRoute = notInRoute.copy()
            newNotInRoute.remove(zone)
            findAllRoutes(newRoute, newNotInRoute, routes)


# generates geoJSON for display of a given route
def generate(request):
    id = json.loads(request.body)['id']
    route = Route.objects.get(id=id)
    geoJSON = route.getGeoJSON()

    return JsonResponse(geoJSON)


