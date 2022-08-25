import django
from django.conf import settings
import os
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TravellingTurfer.settings')
django.setup()



import math
from routing.nearestNeighbour import optimise as nearest_neighbour
from routing.christofides import optimise as christofides
from routing.bruteForce import optimise as brute_force
from routing.twoOpt import optimise as twoopt
from routing.threeOpt import optimise as threeopt
import argparse

algorithms = {'christofides': christofides, 'nearest-neighbour': nearest_neighbour, 'brute-force': brute_force}


def main():

    # interpret CLI context
    parser = argparse.ArgumentParser()
    parser.add_argument("algorithm", type=valid_algorithm, help="use this algortihm")
    parser.add_argument("file", type=valid_file, help="solve tsp problem in this file")
    parser.add_argument("-2", "--twoopt", help="apply 2-opt heuristic to route", action='store_true')
    parser.add_argument("-3", "--threeopt", help="apply 3-opt heuristic to route", action='store_true')
    args = parser.parse_args()

    file = args.file
    algorithm = algorithms[args.algorithm]
    twoopt_bool = args.twoopt
    threeopt_bool = args.threeopt

    # parse problem and optimum solution
    zones = []
    optimum = []
    try:
        with open(file, 'r') as file:
            for line in file:
                if line[0].isdigit() and 'EOF' not in line:
                    data = line.strip().split(' ')
                    zone = Zone(data[0], data[1], data[2])
                    zones.append(zone)
                if line.startswith('OPTIMUM'):
                    optimum = line.strip('OPTIMUM ').strip().split(" ")

    except:
        raise Exception("Problem with file")
                
    # generate distance matrix
    distanceMatrix = {zone.id:{} for zone in zones}
    for start in zones:
        for end in zones:
            distanceMatrix[start.id][end.id] = distanceMatrix[end.id][start.id] = pair_distance(start, end)

    # solve with base algorithm
    try:
        route = algorithm([zone.id for zone in zones], distanceMatrix)
    except Exception:
        route = algorithm([zone.id for zone in zones], distanceMatrix, DummyJob())
    distance = route_distance(route, distanceMatrix)
    print(f"{args.algorithm} generated route of length: {distance}")

    # improvement heuristics
    if twoopt_bool:
        route = twoopt(route, distanceMatrix, DummyJob())
        distance = route_distance(route, distanceMatrix)
        print(f"2-opt improved route to length: {distance}")

    if threeopt_bool:
        route = threeopt(route, distanceMatrix, DummyJob())
        distance = route_distance(route, distanceMatrix)
        print(f"3-opt improved route to length: {distance}")

    # optimum distance
    optimum_distance = route_distance(optimum, distanceMatrix)
    print(f"distance of optimum route: {optimum_distance}")
    print(f"{round((distance/optimum_distance*100)-100, 2)}% above optimal route")



#helper functions/classes
def valid_algorithm(algo):
    if algo not in algorithms:
        raise argparse.ArgumentTypeError(f'must be one of {[key for key in algorithms]}')
    return algo

def valid_file(file):
    try:
        with open(file, 'r'):
            pass
    except:
        raise argparse.ArgumentTypeError('not a valid file')
    return file

def pair_distance(start, end):
    return math.sqrt((end.y - start.y) ** 2 + ((end.x - start.x)) ** 2)

def route_distance(zones, distanceMatrix):
    distance = 0
    for i in range(len(zones)-1):
        distance += distanceMatrix[zones[i]][zones[i+1]]
    return distance

class Zone:
    def __init__(self, id, x, y):
        self.id = id
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"Zone {self.id} at ({self.x},{self.y})"

# mocks Job model
class DummyJob:
    def save(self, *args, **kwargs):
        pass

if __name__ == '__main__':
    main()
