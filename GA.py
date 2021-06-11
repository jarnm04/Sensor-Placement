# Genetic Algorithm to solve the sensor placement problem
# Written by: Joshua Rinaldi
# For: AFIT/ENG CSCE 686, Spring 2021 Final Project

import random
from copy import deepcopy

# Define the objects that will be used for this execution - there are 3, as can be seen
class Candidate(object):
    def __init__(self, geneLen):
        self.gene = []
        for i in range(geneLen):
            self.gene.append(0)
        self.vertices = dict[int, Vertex]
        self.edges = dict[int, Edge]
        self.feasible = False
        self.fitness = 0
        self.kill = False
    
    def __repr__(self):
        return self.gene

class Vertex(object):
    def __init__(self, name, numVulns, neighborList, type):
        self.name = name
        self.numVulns = numVulns
        self.type = type
        self.neighborList = neighborList
        self.vertices = {}
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

# Function to actually make a vertex and return it to the initilization function
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

# This function will initialize the graph, as well as other data structures we want to use
def initializeGraph(fileName):
    # get a file from the user, open it and read the lines
    if not fileName:
        fileName = input("Graph file name: ")
    file = open("{}".format(fileName), 'r')
    file_lines = file.readlines()

    # remove the return character from the end of the lines
    for line in range(len(file_lines)):
        file_lines[line] = file_lines[line].replace('\n', '')

    # some useful data structures that we'll use
    vertices = {}
    edgeNodes = []
    targetNodes = []

    # build out the vertices from the file
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

# function to produce the reduced graph for a candidate
def graphReduction(cand: Candidate, edgesToRemove: list[int]):
    random.shuffle(edgesToRemove)
    while len(edgesToRemove) > 0 and len(cand.vertices) > 2:
        edgeID = edgesToRemove.pop()
        if edgeID in cand.edges.keys():
            edge:Edge = cand.edges[edgeID]
            src:Vertex = edge.source
            dest:Vertex = edge.dest
            
            vNames = []
            for key in cand.vertices.keys():
                vNames.append(key)
            vNames = sorted(vNames, reverse=True)
            newVertName = vNames.pop(0)+1

            numVulns = src.numVulns + dest.numVulns
            newNeighborList = src.neighborList + dest.neighborList
            while src.name in newNeighborList:
                newNeighborList.remove(src.name)
            while dest.name in newNeighborList:
                newNeighborList.remove(dest.name)

            newVert = Vertex(newVertName, numVulns, newNeighborList, "S")
            for v in cand.vertices.keys():
                while src.name in cand.vertices[v].neighborList:
                    cand.vertices[v].neighborList.remove(src.name)
                cand.vertices[v].neighborList.append(newVertName)
                while dest.name in cand.vertices[v].neighborList:
                    cand.vertices[v].neighborList.remove(dest.name)
                cand.vertices[v].neighborList.append(newVertName)
            newVert.numTargs = src.numTargs + dest.numTargs
            newVert.numEdges = src.numEdges + dest.numEdges
            cand.vertices.update({newVertName: newVert})
            candVerts: dict[int, Vertex] = cand.vertices.copy()
            if src.name == dest.name:
                if src.name in candVerts.keys():
                    del candVerts[src.name]
            else:
                if src.name in candVerts.keys():
                    del candVerts[src.name]
                if dest.name in candVerts.keys():
                    del candVerts[dest.name]
            cand.vertices = candVerts

            candEdges: dict[int, Edge] = cand.edges.copy()
            del candEdges[edgeID]
            revEdge = 0
            for e in candEdges:
                if candEdges[e].dest.name == src.name and candEdges[e].source.name == dest.name: revEdge = e
                else:
                    if candEdges[e].dest.name == dest.name: candEdges[e].dest = newVert
                    if candEdges[e].dest.name == src.name: candEdges[e].dest = newVert
                    if candEdges[e].source.name == src.name: candEdges[e].source = newVert
                    if candEdges[e].source.name == dest.name: candEdges[e].source = newVert
            if revEdge != 0:
                del candEdges[revEdge]
                cand.gene[revEdge - 1] = 0
            cand.edges = candEdges

    for edgeID in edgesToRemove:
        cand.gene[edgeID-1] = 1

    return(cand)


# feasibilty function, will change the feasibility if candidate is feasible
def feasibility(cand: Candidate):
    if len(cand.vertices) > 2:
        cand.feasible = False
    elif len(cand.vertices) == 2:
        cand.feasible = True

# Repair function
def repair(cand: Candidate):
    feasibility(cand)
    while cand.feasible == False:
        # ensure the edges appearing in the candidate gene are actually contained in the array....
        # tempDict = {}
        # for a in range(len(cand.gene)):
        #     if cand.gene[a] == 1:
        #         tempDict[a+1] = edges[a+1]
        # cand.edges = tempDict

        # randomly choose an edge to remove by flipping the associated allele to a 0
        if len(cand.edges) == 0:
            cand.kill = True
            break
        e_key = random.choice(list(cand.edges.keys()))
        cand.gene[e_key-1] = 0

        # create new graph reduction and check feasibility again
        edgesToRemove = []
        for a in range(len(cand.gene)):
            if cand.gene[a] == 0 and (a+1) in list(cand.edges):
                edgesToRemove.append(a+1)
        cand = graphReduction(cand, edgesToRemove)
        feasibility(cand)

    return(cand)

# This initializes the candidate population
def initializePop(vertices: dict[int, Vertex], edges: dict[int, Edge]):
    geneLen = len(edges)
    candidatePopulation = []
    for _ in range(50):
        newCand = Candidate(geneLen)
        seedNum = random.randint(0, geneLen-1) / geneLen

        for i in range (geneLen):
            if (random.randint(0,100)/100) <= seedNum:
                newCand.gene[i] = 1

        newCand.vertices = deepcopy(vertices)
        newCand.edges = deepcopy(edges)

        edgesToRemove = []
        for a in range(len(newCand.gene)):
            if newCand.gene[a] == 0:
                edgesToRemove.append(a+1)
        graphReduction(newCand, edgesToRemove)
        newCand = repair(newCand)
        if newCand.kill == False:
            candidatePopulation.append(newCand)

    return candidatePopulation

def evaluate(pop: list[Candidate], numGraphEdges, numGraphTargs):
    killList = []
    for cand in pop:
        if cand.kill == True:
            killList.append(cand)
    for cand in killList:
        if cand in pop:
            pop.remove(cand)
    if len(cand.edges) == 0:
        print("we got one")
    for cand in pop:
        vert: Vertex = random.choice(list(cand.vertices.values()))
        edge_delta = vert.numEdges / numGraphEdges
        target_delta = vert.numTargs / numGraphTargs
        cand.fitness = (abs(edge_delta - target_delta) / len(cand.edges))

    return(pop)



def selection(pop: list[Candidate]):
    numRemove = len(pop) - 50
    if numRemove > 0:
        pop.sort(key=lambda c: c.fitness, reverse=False)
        for i in range(numRemove):
            pop.pop(0)
    
    return(pop)


def mutate(child: Candidate, p1: Candidate, p2: Candidate):
    magChild = 0
    for allele in child.gene:
        if allele == 1: magChild += 1
    mu = 1 - ( ( 0.5 * ( len(p1.edges) + len(p2.edges) ) ) / magChild )

    for a in range(len(child.gene)):
        odds = (random.randint(0,100)) / 100
        if odds < mu:
            if child.gene[a] == 1: child.gene[a] == 0
            elif child.gene[a] == 0: child.gene[a] == 1

    return child

def crossover(pop: list[Candidate], vertices: dict[int, Vertex], edges: dict[int, Edge]):
    breeders = []
    breederIdx = []
    for _ in range(10):
        idx = random.randint(0, len(pop)-1)
        while idx in breederIdx:
            idx = random.randint(0, len(pop)-1)
        
        breederIdx.append(idx)
        breeders.append(pop[idx])

    while len(breeders) > 0:
        p1 = breeders.pop(0)
        p2 = breeders.pop(0)

        p1gene = int("".join(str(i) for i in p1.gene),2)
        p2gene = int("".join(str(i) for i in p2.gene),2)

        offspringGeneBin = bin(p1gene | p2gene)

        offspringGene = [int(d) for d in str(offspringGeneBin)[2:]]

        diff = len(p1.gene) - len(offspringGene)
        if diff > 0:
            for _ in range(diff):
                offspringGene.insert(0,0)

        offspring = Candidate(len(edges))
        
        offspring.gene = offspringGene
        offspring.vertices = deepcopy(vertices)
        offspring.edges = deepcopy(edges)

        offspring = mutate(offspring, p1, p2)
        offspring = repair(offspring)
        if len(offspring.edges) == 0: offspring.kill = True        
        if offspring.kill == False:
            pop.append(offspring)
    
    return (pop)

def likelihood(edge: Edge, n, vertices: dict[int, Vertex]):
    dest: Vertex = edge.dest
    cumVulnNext = 0
    for n in dest.neighborList:
        cumVulnNext += vertices[n].numVulns
    edge.likelihood = dest.numVulns * (cumVulnNext / n)
    return edge


# Main loop of the program
def GADriver(file = None, numSensor = None):
    # first up, initialize the graph file and pull relevant data out of .txt file
    (vertices, edgeNodes, targetNodes, edges) = initializeGraph(file)

    if not numSensor:
        numSensor = input("Number of available sensors: ")
    numSensor = int(numSensor)

    # now initialize the candidate population
    candidatePopulation = initializePop(vertices, edges)

    # breed new generations of candidates
    for _ in range(50):
        candidatePopulation = evaluate(candidatePopulation, len(edgeNodes), len(targetNodes))
        candidatePopulation = selection(candidatePopulation)
        candidatePopulation = crossover(candidatePopulation, vertices, edges)

    candidatePopulation = evaluate(candidatePopulation, len(edgeNodes), len(targetNodes))
    fittestCand: Candidate = candidatePopulation.pop(0)
    
    fittestCandEdges = []
    for e in range(len(fittestCand.gene)):
        if fittestCand.gene[e] == 1:
            fittestCandEdges.append(edges[e+1])
    
    for e in fittestCandEdges:
        e = likelihood(e, len(fittestCandEdges), vertices)

    fittestCandEdges.sort(key=lambda e: e.likelihood, reverse=True)

    solution = []

    while len(fittestCandEdges) > 0:
        solEdge = fittestCandEdges.pop(0)
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