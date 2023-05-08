

def distance(route, distanceMatrix):
    distance = 0.0

    for i, zone in enumerate(route):
        if i != len(route)-1:
            distance += distanceMatrix[zone][route[i+1]]
    
    return distance

