import itertools
from math import dist, perm

def optimise(zones, distanceMatrix):

    MST = minimumSpanningTree(zones, distanceMatrix)
    oddDegreeVertices = findOddDegreeVertices(MST)
    eulerianMultigraph = generateEulerianMultigraph(MST, oddDegreeVertices, distanceMatrix)
    eulerTour = fleury(eulerianMultigraph)
    route = hamiltonian(eulerTour)
    route.append(route[0])
    return route


def minimumSpanningTree(zones, distanceMatrix):

        MST = {zone:{} for zone in zones}
        numberVertices = len(zones)
        numberEdges = 0
        inTree = [zones[0],]
        notInTree = [zones[i] for i in range(1,len(zones))]

        while numberEdges < numberVertices - 1:
            closestZone = None
            closestDistance = 0
            fromZone = None
            for zone_a in inTree:
                for zone_b in notInTree:
                    distance = distanceMatrix[zone_a][zone_b]
                    if not closestZone or distance < closestDistance:
                        closestDistance = distance
                        closestZone = zone_b 
                        fromZone = zone_a
            inTree.append(closestZone)
            notInTree.remove(closestZone)

            MST[fromZone][closestZone] = 1
            MST[closestZone][fromZone] = 1

            numberEdges += 1

        return MST


def findOddDegreeVertices(MST):
    oddDegreeVertices = []
    for node in MST:
        if len(MST[node]) % 2 == 1:
            oddDegreeVertices.append(node)

    return oddDegreeVertices


def generateEulerianMultigraph(MST, oddDegreeVertices, distanceMatrix):
    bipartiteSplits = generateSplits(oddDegreeVertices)
    perfectMatch = perfectMatching(bipartiteSplits, distanceMatrix)
    eulerianMultiGraph = MST.copy()

    for edge in perfectMatch:
        start = edge
        end = list(perfectMatch[edge].keys())[0]
        try:
            eulerianMultiGraph[start][end] = eulerianMultiGraph[start][end] + 1
        except:
            eulerianMultiGraph[start][end] = 1

    return eulerianMultiGraph


def generateSplits(oddDegreeVertices):

    permutations = list(itertools.combinations(oddDegreeVertices, r=int(len(oddDegreeVertices)/2)))
    length = len(permutations)
    splits = []

    for i in range(int(length/2)):
        splits.append((permutations[i], permutations[length - 1 - i]))

    return splits


def perfectMatching(bipartiteSplits, distanceMatrix):

    bestMatch = {}
    bestDistance = 0

    for split in bipartiteSplits:
        match = bestMatching(split, distanceMatrix)

        splitBestMatchingGraph = match['graph']
        splitBestMatchingDistance = match['distance']

        if splitBestMatchingDistance < bestDistance or not bestMatch:
            bestMatch = splitBestMatchingGraph
            bestDistance = splitBestMatchingDistance

    return bestMatch


def bestMatching(split, distanceMatrix):

    bestMatching = {}
    bestDistance = 0

    permutationsSetOne = list(itertools.combinations(split[0], r = int(len(split[0]))))
    permutationsSetTwo = list(itertools.combinations(split[1], r = int(len(split[1]))))

    for permutationOne in permutationsSetOne:

        for permutationTwo in permutationsSetTwo:

            matching = {zone:{} for zone in (permutationOne + permutationTwo)}
            distance = 0

            for i, zoneOne in enumerate(permutationOne):

                zoneTwo = permutationTwo[i]

                matching[zoneOne][zoneTwo] = 1
                matching[zoneTwo][zoneOne] = 1

                distance += distanceMatrix[zoneOne][zoneTwo]

            if distance < bestDistance or not bestMatching:

                bestDistance = distance
                bestMatching = matching

    results = {'graph': bestMatching, 'distance': distance}
    return results


def fleury(eulerianMultiGraph):

    tour = []
    start = list(eulerianMultiGraph.keys())[0]
    findTour(start, tour, copy(eulerianMultiGraph))

    return tour

def findTour(start, tour, eulerianMultiGraph):

    for end in eulerianMultiGraph[start]:

        if end != start and eulerianMultiGraph[start][end] > 0:

            if validStep(start, end, eulerianMultiGraph):

                # add step to tour
                tour.append(end)

                # remove edge
                eulerianMultiGraph[start][end] = eulerianMultiGraph[start][end] - 1
                eulerianMultiGraph[end][start] = eulerianMultiGraph[end][start] - 1
                findTour(end, tour, eulerianMultiGraph)


def validStep(start, end, eulerianMultiGraph):

    numberEdgesFromStart = 0

    for end in eulerianMultiGraph[start]:
        numberEdgesFromStart += eulerianMultiGraph[start][end]

    # this step is the only option
    if numberEdgesFromStart == 1:
        return True
    else:
        # count nodes reachable from start
        reachableFromStart = reachableNodes(copy(eulerianMultiGraph), start, None)

        # remove edge start to end
        tempCopy = copy(eulerianMultiGraph)

        tempCopy[start][end] -= 1
        tempCopy[end][start] -= 1

        # count nodes reachable from start
        reachableFromStartWithoutEdge = reachableNodes(copy(eulerianMultiGraph), start, None)

        # add back to graph
        tempCopy[start][end] += 1
        tempCopy[end][start] += 1

        # if first count greater then this edge is a bridge 
        if reachableFromStart > reachableFromStartWithoutEdge:
            # start -> end is a bridge
            return False
        return True
   

def reachableNodes(multigraph, node, prevNode):
    count = {node,}

    # mark as visited
    if prevNode:
        multigraph[prevNode][node] -= 1
        multigraph[node][prevNode] -= 1

    for nextNode in multigraph[node]:
        if multigraph[node][nextNode] > 0:
            count.update(reachableNodes(multigraph, nextNode, node))

    return count

def hamiltonian(eulerTour):
    hamiltonian = []
    for zone in eulerTour:
        if zone not in hamiltonian:
            hamiltonian.append(zone)

    return hamiltonian


def copy(multigraph):
    copy = {}
    for start in multigraph:
        copy.update({start: {}})
        for end in multigraph[start]:
            copy[start][end] = multigraph[start][end]
    return copy