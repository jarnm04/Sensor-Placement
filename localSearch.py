# Tabu Search to solve the sensor placement problem
# Written by: Joshua Rinaldi
# For: AFIT/ENG CSCE 686, Spring 2021 Final Project

from os import name
import random
import math
from copy import deepcopy

class Neighbor(object):
    def __init__(self, geneLen):
        self.gene = []
        for _ in range(geneLen):
            self.gene.append(1)
        self.vertices = dict[int, Vertex]
        self.edges = dict[int, Edge]
        self.fitness = None
        self.alteredAllele = None

    def __repr__(self):
        return self.gene

class Vertex(object):
    def __init__(self, name, numVulns, neighborList, type):
        self.name = name
        self.numVulns=  numVulns
        self.neighborList = neighborList
        self.type = type
        self.numTargs = 0
        self.numEdges = 0

    def __str__(self) -> str:
        return str(self.name)

class Edge(object):
    def __init__(self, id, source, dest, weight):
        self.id = id
        self.source: Vertex = source
        self.dest: Vertex = dest
        self.weight = weight
        self.likelihood = 0

def makeVertex(file_lines):
    name = file_lines.pop(0)
    name = int(name)
    type = file_lines.pop(0)
    numVulns = file_lines.pop(0)
    numVulns = int(numVulns)
    numNeighbors = file_lines.pop(0)
    numNeighbors = int(numNeighbors)
    neighborList = []
    while file_lines[0] != "#":
        n = file_lines.pop(0)
        n = int(n)
        if n != name:
            neighborList.append(n)
    file_lines.pop(0)
    newVertex = Vertex(name, numVulns, neighborList, type)

    return newVertex

def initializeGraph(filename = None):
    if not filename:
        filename = input("Graph file name: ")
    file = open("{}".format(filename), 'r')
    file_lines = file.readlines()

    for line in range(len(file_lines)):
        file_lines[line] = file_lines[line].replace('\n', '')

    vertices = {}
    edgeNodes = []
    targetNodes = []

    while len(file_lines) > 0:
        vertex = makeVertex(file_lines)
        vertices[vertex.name] = vertex
        if vertex.type == "E":
            vertex.numEdges = 1
            edgeNodes.append(vertex)
        elif vertex.type == "T":
            vertex.numTargs = 1
            targetNodes.append(vertex)

    file.close()

    edges = {}
    edgeID = 1
    for v in vertices:
        for n in vertices[v].neighborList:
            weight = vertices[n].numVulns
            newEdge = Edge(edgeID, deepcopy(vertices[v]), deepcopy(vertices[n]), weight)
            edges[edgeID] = newEdge
            edgeID += 1

    return (vertices, edgeNodes, targetNodes, edges)

def graphReduction(seed: Neighbor, edgesToRemove: list[int]):
    # pull the vertice and edge list into convenience variables
    verts: dict[int, Vertex] = seed.vertices
    edges: dict[int, Edge] = seed.edges

    while len(verts) > 2 and len(edgesToRemove) > 0 and len(edges) > 1:
        # pop first eID from list of edges to remove (there should only be one value here after the seed is created)
        eID = edgesToRemove.pop(0)

        # pull relevant info into more convenience variables
        edgeR: Edge = edges[eID]
        srcVert: Vertex = deepcopy(edgeR.source)
        destVert: Vertex = deepcopy(edgeR.dest)

        # create new vertex name - just increment the largest vertex name by one
        vNames = []
        for key in list(seed.vertices.keys()):
            vNames.append(key)
        vNames = sorted(vNames, reverse=True)
        newVertName = vNames.pop(0)+1

        # update edge values, also remove any self edges
        selfEdgeKeys = []
        for e in edges.keys():
            changeSource = False
            changeDest = False
            if edges[e].source.name == srcVert.name or destVert.name: changeSource = True
            if edges[e].dest.name == srcVert.name or destVert.name: changeDest = True

            if changeSource:
                edges[e].source.name = newVertName
            if changeDest:
                edges[e].dest.name = newVertName
            if changeSource and changeDest:
                selfEdgeKeys.append(e)

        for key in selfEdgeKeys:
            edges.pop(key)

        # create the needed values for the seed
        newNumTargs = srcVert.numTargs + destVert.numEdges
        newNumEdges = srcVert.numEdges + destVert.numEdges
        newNumVulns = srcVert.numVulns + destVert.numVulns
        newNeighborList = srcVert.neighborList + destVert.neighborList
        newNeighborList = list(set(newNeighborList))
        while srcVert.name in newNeighborList:
            newNeighborList.remove(srcVert.name)
        while destVert.name in newNeighborList:
            newNeighborList.remove(destVert.name)

        # build the new seed with the values create above
        newVert: Vertex = Vertex(newVertName, newNumVulns, newNeighborList, "S")
        newVert.numEdges = newNumEdges
        newVert.numTargs = newNumTargs

        # remove old vertices from the vertex list, add new verex to the list
        verts.pop(srcVert.name)
        verts.pop(destVert.name)
        verts[newVertName] = newVert

    # in case of initial seed value - any edges not removed should be added back in
    # update other values and return seed to caller
    for eID in edgesToRemove:
        seed.gene[eID -1] = 1
    seed.edges = edges
    seed.vertices = verts
    return seed

def evaluate(neigh: Neighbor, added: bool, numEdgeNodes, numTargNodes):
    usingVertIdx= random.choice(list(neigh.vertices.keys()))
    usingVert = neigh.vertices[usingVertIdx]
    edge_delta = usingVert.numEdges / numEdgeNodes
    targ_delta = usingVert.numTargs / numTargNodes

    if added:
        neigh.fitness = -1 + abs(edge_delta - targ_delta)
    elif not added:
        neigh.fitness = 1 + abs(edge_delta - targ_delta)

    return neigh

def generateSeed(vertices: dict[int, Vertex], edges: dict[int, Edge]):
    # intialize the seed for the algo
    geneLen = len(edges)
    seed: Neighbor = Neighbor(geneLen)
    temp = 0.25 * geneLen
    temp = int(math.ceil(temp))
    numFlip = random.randint(0,temp)

    # to start, randomly remove no more than a quarter of the edges from the graph
    temp = geneLen - 1
    a = random.randint(0,temp)
    edgesToRemove = []
    for _ in range(numFlip):
        while seed.gene[a] == 0:
            a = random.randint(0,temp)
        seed.gene[a] = 0
        edgesToRemove.append(a+1)

    # insert the complete list of verts and edges into the seed
    seed.vertices = deepcopy(vertices)
    seed.edges = deepcopy(edges)

    random.shuffle(edgesToRemove)
    seed = graphReduction(seed, edgesToRemove)

    return seed

def generateNeighbors(curSol: Neighbor, vertices: dict[int, Vertex], edges: dict[int, Edge], numEdgeNodes, numTargNodes):
    #TODO implement
    neighborhood = []

    # loop over the gene, creating a new neighbor for every possible allele change that could happen
    for idx in range(len(curSol.gene)):
        # initialize the new neighbor with the shift in genes
        newNeigh: Neighbor = Neighbor(len(curSol.gene))
        newNeigh.gene = deepcopy(curSol.gene)
        newNeigh.vertices = deepcopy(vertices)
        newNeigh.edges = deepcopy(edges)

        # change the appropriate allele
        added = False
        if newNeigh.gene[idx] == 0:
            newNeigh.gene[idx] = 1
            added = True
        elif newNeigh.gene[idx] == 1: newNeigh.gene[idx] = 0
        # this will help with tabu list
        newNeigh.alteredAllele = idx

        # determine edges to remove and perform graph reduction on newNeigh
        edgesToRemove = []
        for a in range(len(newNeigh.gene)):
            if newNeigh.gene[a] == 0:
                edgesToRemove.append(a+1)
        newNeigh = graphReduction(newNeigh, edgesToRemove)

        newNeigh = evaluate(newNeigh, added, numEdgeNodes, numTargNodes)

        neighborhood.append(newNeigh)

    neighborhood.sort(key=lambda n: n.fitness, reverse=True)

    return neighborhood


def likelihood(edge: Edge, n, vertices: dict[int, Vertex]):
    dest: Vertex = edge.dest
    cumVulnNext = 0
    for n in dest.neighborList:
        cumVulnNext += vertices[n].numVulns
    edge.likelihood = dest.numVulns * (cumVulnNext / n)
    return edge

def localSearchDriver(file = None, numSensor = None):
    (vertices, edgeNodes, targetNodes, edges) = initializeGraph(file)

    if not numSensor:
        numSensor = input("Number of available sensors: ")
    numSensor = int(numSensor)

    curSol = generateSeed(vertices, edges)
    curSol = evaluate(curSol, False, len(edgeNodes), len(targetNodes))

    split = False
    noImprovementIdx = 0
    tabuList: dict[int, int] = {}
    # this is what will determine how long a value must live in the tabu list
    # tabu lenght will be four provided a sufficient number of edges
    tabuLength = 0.25 * len(edges)
    if tabuLength > 4: tabuLength = 4
    
    curFittest = curSol

    firstIteration = True

    while noImprovementIdx < 10 and split == False:
        # decrement time each move has remaining in tabu list & remove from list if it has stayed long enough
        if not firstIteration:
            freeKeys = []
            for key in tabuList.keys():
                tabuList[key] -= 1
                if tabuList[key] <= 0:
                    freeKeys.append(key)
            for key in freeKeys:
                tabuList.pop(key)
        neighborhood: list[Neighbor] = generateNeighbors(curSol, vertices, edges, len(edgeNodes), len(targetNodes))
        nextSol:Neighbor = neighborhood.pop(0)
        while nextSol.alteredAllele in list(tabuList.keys()):
            nextSol = neighborhood.pop(0)
        if nextSol.fitness > curFittest.fitness:
            curFittest = nextSol
            noImprovementIdx = -1
        tabuList[nextSol.alteredAllele] = tabuLength
        curSol = nextSol
        if len(curSol.vertices) == 2:
            split = True
        noImprovementIdx += 1
        firstIteration = False

    fittestNeighEdges = []
    for e in range(len(curFittest.gene)):
        if curFittest.gene[e] == 1:
            fittestNeighEdges.append(edges[e+1])

    for e in fittestNeighEdges:
        e = likelihood(e, len(fittestNeighEdges), vertices)
    
    fittestNeighEdges.sort(key=lambda e: e.likelihood, reverse=True)

    solution = []

    while len(fittestNeighEdges) > 0:
        solEdge = fittestNeighEdges.pop(0)
        solution.append([solEdge.source.name, solEdge.dest.name])

    for e in range(len(solution)):
        solution[e] = sorted(solution[e])

    solReduc = []
    [solReduc.append(e) for e in solution if e not in solReduc]

    print("Edges to cover: ")
    for _ in range(numSensor):
        if len(solReduc) > 0:
            print(solReduc[0])
            solReduc.pop(0)



# main()

# print("Finished Execution")