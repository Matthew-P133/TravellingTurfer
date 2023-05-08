import routing.routing_utils as routing_utils

def optimise(route, distanceMatrix, job):
    distance = routing_utils.distance(route, distanceMatrix)
    while True:
        optimised = True
        for i, zone in enumerate(route):
            if (i > 0 and i < len(route)-1):
                for j, zoneTwo in enumerate(route):
                    if j > 0 and j < len(route)-1 and zone != zoneTwo:
                        temp = zone
                        route[i] = zoneTwo
                        route[j] = temp
                        if routing_utils.distance(route, distanceMatrix) < distance:
                            distance = routing_utils.distance(route, distanceMatrix)
                            job.shortest = distance
                            job.save()
                            optimised = False
                            break
                        temp = route[i]
                        route[i] = route[j]
                        route[j] = temp
        if optimised:
            break
    return route
            

