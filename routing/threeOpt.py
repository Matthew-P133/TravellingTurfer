import itertools
from math import dist
import routing.routing_utils as routing_utils

def optimise(route, distanceMatrix):
    distance = routing_utils.distance(route, distanceMatrix)
    while True:
        optimised = True
        for i, zone in enumerate(route):
            if not optimised:
                break
            if (i > 0 and i < len(route)-1):
                for j, zoneTwo in enumerate(route):
                    if not optimised:
                        break
                    if j > 0 and j < len(route)-1 and zone != zoneTwo:
                        for k, zoneThree in enumerate(route):
                            if not optimised:
                                break
                            if k > 0 and k < len(route)-1 and zoneThree != zoneTwo and zoneThree != zone:
                                permutations = itertools.permutations([zone, zoneTwo, zoneThree], 3)
                                tempOne = zone
                                tempTwo = zoneTwo
                                tempThree = zoneThree
                                for permutation in list(permutations):
                                    route[i] = permutation[0]
                                    route[j] = permutation[1]
                                    route[k] = permutation[2]
                                    if routing_utils.distance(route, distanceMatrix) < distance:
                                        distance = routing_utils.distance(route, distanceMatrix)
                                        optimised = False
                                        break
                                if not optimised:
                                    break
                                route[i] = tempOne
                                route[j] = tempTwo
                                route[k] = tempThree
        if optimised:
            break
    return route
            