# This is the deterministic approach to solving the sensor placement problem
# Written by: Joshua Rinaldi
# AFIT/ENG CSCE 686, Spring 2021 Final Project

# Object class for the vertex

class Vertex(object):
    def __init__(self, name, numVulns, neighborList, type, numNeighbors ):
        self.name = name
        self.numVulns = numVulns
        self.neighbors = {}
        self.neighborList = neighborList
        self.numNeighbors = numNeighbors
        self.type = type

    def __str__(self) -> str:
        return str(self.name)

# This will read through the file until it hits a stopping character, creating a new vertex
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
        neighborList.append(n)
    file_lines.pop(0)
    newVertex = Vertex(name, numVulns, neighborList, type, numNeighbors)

    return newVertex


# Initialization function. It will ingest a user indicated file and return that as a useable
# array of vertices in the graph
def initializeGraph(fileName = None):
    if not fileName:
        fileName = input("Graph file name: ")
    file = open("{}".format(fileName), 'r')
    file_lines = file.readlines()

    # removes return character from lines
    for line in range(0,len(file_lines)):
        file_lines[line] = file_lines[line].replace('\n', '')

    vertices = []
    edgeNodes = []
    targetNodes = []

    while len(file_lines) > 0:
        vertex = makeVertex(file_lines)
        vertices.append(vertex)
        if vertex.type == "E": edgeNodes.append(vertex)
        elif vertex.type == "T": targetNodes.append(vertex)

    file.close()

    # now that all vertexes are made, create dictionary mapping each neighbor to the vertex object for that neighbor
    # this is done, instead of a matrix as indicated in the paper for simplicity's sake
    for vertex in vertices:
        for n in vertex.neighborList:
            for v in vertices:
                if n == v.name:
                    vertex.neighbors[n] = v

    return (vertices, edgeNodes, targetNodes)

# this function computes the likelihood of moving to the next node
def likelihood(vertex, path):
    vertInPath = 1
    if vertex in path:
        vertInPath = 0
    
    sumNeighVulns = 0
    numNeighs = 0
    for neigh in vertex.neighbors:
        if (neigh in path) == False:
            sumNeighVulns += vertex.neighbors[neigh].numVulns
            numNeighs += 1
    
    likelihood = vertInPath * vertex.numVulns * (sumNeighVulns / numNeighs)

    return likelihood

# This function will actually do the finding of paths through network
def findPaths(path, vertices, targetNodes, edgesofInterest):
    vCur = path[len(path)-1]
    if vCur in targetNodes:
        # append edges to the edgesOfInterest list
        # up to this point, paths are just a series of vertices, edges will be defined as a tuple
        # (s, d, w), where s = source vertex, d = destination vertex, w = weight = vuln of dest
        totalVulns = 0
        for v in path:
            totalVulns += v.numVulns
        pathScore = totalVulns / (len(path) ** 3)
        
        for e in range(len(path)-1):
            newEdge = "{},{}".format(path[e].name, path[e+1].name)
            if newEdge in edgesofInterest:
                edgesofInterest[newEdge] += pathScore
            else:
                edgesofInterest[newEdge] = pathScore


    else:
        likelihoods = []
        for neighbor in vCur.neighbors:
            l_neigh = likelihood(vCur.neighbors[neighbor], path)
            likelihoods.append((neighbor, l_neigh))
        likelihoods = sorted(likelihoods,key=lambda x:(-x[1]))
        
        for next in likelihoods:
            if next[1] != 0:
                newPath = path.copy()
                newPath.append(vCur.neighbors[next[0]])
                findPaths(newPath, vertices, targetNodes, edgesofInterest)




def determDriver(file = None, numSens = None):
    # first up, ingest the graph file and create the data and data structures that we'll need
    (vertices, edgeNodes, targetNodes) = initializeGraph(file)
    edgesOfInterest = {}
    if not numSens:
        numSens = input("Number of available sensors: ")
    numSens = int(numSens)
    solutionSet = []

    # find all potential paths from edge nodes to target nodes
    for node in edgeNodes:
        path = []
        path.append(node)
        findPaths(path, vertices, targetNodes, edgesOfInterest)

    # pull the most likely edges out of edgesOfInterest and return them
    listOfEdges = []
    # print("Our edges of interest are:")
    for edge in edgesOfInterest:
        listOfEdges.append((edge, edgesOfInterest[edge]))
        # print("edge: {}, edge score: {}".format(edge, edgesOfInterest[edge]))

    listOfEdges = sorted(listOfEdges,key=lambda x:(-x[1]))

    for i in range(numSens):
        solutionSet.append(listOfEdges.pop(0))
    
    print("\nThe edges to places sensors on are: ")
    for i in range(len(solutionSet)):
        print("{}".format(solutionSet[i][0]))

# determDriver()

# print("Finished Execution")