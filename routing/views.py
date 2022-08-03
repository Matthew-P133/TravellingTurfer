from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.urls import reverse
import requests
import json
from routing.models import Waypoints, Zone, Distance, Route, Job, createRoute, generateDistanceMatrix
import routing.bruteForce as bruteForce
import routing.nearestNeighbour as nearestNeighbour
import routing.christofides as christofides
import routing.twoOpt as twoOpt
import routing.threeOpt as threeOpt
import routing.routing_utils as routing_utils
import time
import threading



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
    if (abs(northEastLat - southWestLat) < 0.4 and abs(northEastLong - southWestLong) < 1.5):
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

        route = Route()
        route.save()
        job = Job(route=route)
        job.save()

        # start route optimisation job in a new thread and return route id to client
        t = threading.Thread(target=optimisation_job, args=[route, zones, job])
        t.setDaemon(False)
        t.start()   

        # returns route id of newly created route; javascript redirects user to route page
        return HttpResponse(route.id)

    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

def status(request):
    id = json.loads(request.body)[0]
    job = Job.objects.filter(route=Route.objects.get(id=id))
    response = job.values()[0]

    return JsonResponse(response)

def optimisation_job(route, zones, job):

        job.message = f"Generating distance matrix (0 of {len(zones)*len(zones)}"
        job.save()

        # populate distance matrix from database
        start = time.time()
        distanceMatrix = generateDistanceMatrix(zones, job)
        end = time.time()
        job.distance_matrix_generation_ms = end - start
        job.save()
    
        # main algorithm
        start = time.time()
        if len(zones) <= 7:
            job.method = "Bruteforce"
            job.save()
            shortestRoute = bruteForce.optimise(zones, distanceMatrix)
        elif len(zones) <= 40:
            job.method = "Christofide's"
            job.save()
            shortestRoute = christofides.optimise(zones, distanceMatrix, job)
        else:
            job.method = "Nearest Neighbour"
            job.save()
            shortestRoute = nearestNeighbour.optimise(zones, distanceMatrix)
        end = time.time()
        job.base_distance = routing_utils.distance(shortestRoute, distanceMatrix)
        job.base_algorithm_ms = end - start
        job.save()
        
        # extra heuristics
        if len(zones) > 7:
            job.message = "Optimising with 2-opt"
            job.two_opt = True
            job.save()
            start = time.time()
            shortestRoute = twoOpt.optimise(shortestRoute, distanceMatrix, job)
            end = time.time()
            job.two_opt_improvement = job.base_distance - job.shortest
            job.two_opt_ms = end - start
            job.save()

            if len(zones) < 75:
                job.message = "Optimising with 3-opt"
                job.three_opt = True
                job.save()
                start = time.time()
                shortestRoute = threeOpt.optimise(shortestRoute, distanceMatrix, job)
                end = time.time()
                job.three_opt_improvement = job.base_distance - job.two_opt_improvement - job.shortest
                job.three_opt_ms = end - start
                job.save()

        # save route to the database
        route = createRoute(route, shortestRoute)
        job.message = "Optimisation completed"
        job.status = True
        job.save()

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
            route = Route.objects.get(id=id[0])
            geoJSON = route.getGeoJSON()
            waypoints = Waypoints.objects.filter(route=route)
            zones = Zone.objects.filter(id__in=[waypoint.zone_id for waypoint in waypoints]).values()
            waypointsDict = {}

            for waypoint in waypoints:
                if not waypoint.zone_id in waypointsDict or waypoint.position == 0:
                    waypointsDict.update({waypoint.zone_id: waypoint.position})

            for zone in zones:
                zone['position'] = waypointsDict[zone['id']]

            response = {'geoJSON': geoJSON, 'zones': list(zones)}
            return JsonResponse(response)
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST'])

# changes the start/end zone for a route, or reverses the route
def update(request):

    if request.method == 'POST':
        # check request data
        try:
            data = json.loads(request.body)
            route_id = data['id']
            zone_id = data['zone_id']
        except:
            return HttpResponseBadRequest()
        if not len(data) == 2 or not all(key in data for key in ['id', 'zone_id']):
            return HttpResponseBadRequest()
        try:
            route = Route.objects.get(id=route_id)
            waypoints = Waypoints.objects.filter(route=route).order_by('position')

            offset = waypoints.filter(zone_id=zone_id)[0].position
            route_length = len(waypoints)

            # start (or end) zone selected; reverse route direction
            if offset == 0 or offset == route_length-1:
                for i, waypoint in enumerate(waypoints):
                    waypoint.position = route_length - 1 - i
                    waypoint.save()
            # change start point of route 
            else:
                Waypoints.objects.filter(route_id=route_id, position=route_length-1).delete()
                for waypoint in Waypoints.objects.filter(route=route):
                    current_position = waypoint.position
                    new_position = current_position - offset
                    if new_position == 0:
                        Waypoints.objects.create(route_id=route_id, position=route_length-1, zone_id=zone_id)
                    if new_position < 0:
                        new_position = route_length + new_position - 1
                    waypoint.position = new_position
                    waypoint.save()
            return HttpResponse()
        except:
            return HttpResponseBadRequest()
    else:    
        return HttpResponseNotAllowed(permitted_methods=['POST'])


