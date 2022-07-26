from routing.models import Waypoints, Zone, Distance, Route

def optimise(zones, distanceMatrix):

    routeLength = len(zones)

    # add first zone to route
    route = [zones[0],]

    # zones still to be visited
    notInRoute = [zones[i] for i in range(1,routeLength)]

    # add nearest zone to route

    while len(notInRoute) > 0:
        step(route, notInRoute, distanceMatrix)

    # ensure route goes back to start
    route.append(route[0])
    
    return route



def step(route, notInRoute, distanceMatrix):

    start = route[-1]

    nearestNeighbour = None
    nearestNeighbourDistance = 0

    for zone in notInRoute:
        end = zone
        distance = distanceMatrix[start][end]

        if distance < nearestNeighbourDistance or not nearestNeighbour:
            nearestNeighbour = zone
            nearestNeighbourDistance = distance

    route.append(nearestNeighbour)
    notInRoute.remove(nearestNeighbour)
    



def routeDistance(route):

    distance = 0
    for i, zone in enumerate(route):
        if i != len(route)-1:
            start = Zone.objects.get(id=route[i])
            end = Zone.objects.get(id=route[i+1])
            distance += Distance.objects.get(zone_a=start, zone_b=end).distance

    return distance
