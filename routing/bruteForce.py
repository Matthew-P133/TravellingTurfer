from routing.models import Waypoints, Zone, Distance, Route

def optimise(zones, distanceMatrix):

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
        distance = routeDistance(route, distanceMatrix)
        if (distance < shortestDistance or shortestDistance == 0):
            shortestDistance = distance
            shortestRoute = route

    return shortestRoute
    

def routeDistance(route, distanceMatrix):

    distance = 0
    for i, zone in enumerate(route):
        if i != len(route)-1:
            start = route[i]
            end = route[i+1]
            distance = distanceMatrix[start][end]

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
