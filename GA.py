# Genetic Algorithm to solve the sensor placement problem
# Written by: Joshua Rinaldi
# For: AFIT/ENG CSCE 686, Spring 2021 Final Project

import random
import math
import operator
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
    
    def __repr__(self):
        return self.gene

class Vertex(object):
    def __init__(self, name, numVulns, neighborList, type):
        self.name = name
        self.numVulns = numVulns
        self.type = type
        self.neighborList = neighborList
        self.vertices = {}

    def __str__(self) -> str:
        return str(self.name)

class Edge(object):
    def __init__(self, id, source, dest, weight):
        self.id = id
        self.source = source
        self.dest = dest
        self.weight = weight

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
def initializeGraph():
    # get a file from the user, open it and read the lines
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
        if vertex.type == "E": edgeNodes.append(vertex)
        elif vertex.type == "T": targetNodes.append(vertex)

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
    for edgeID in edgesToRemove:
        if len(cand.vertices) == 2:
            for eID in cand.edges.keys():
                cand.gene[eID-1] = 1
            break
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
            cand.vertices.update({newVertName: newVert})
            candVerts: dict[int, Vertex] = cand.vertices.copy()
            del candVerts[src.name]
            del candVerts[dest.name]
            cand.vertices = candVerts

            candEdges: dict[int, Edge] = cand.edges.copy()
            del candEdges[edgeID]
            revEdge = 0
            for e in candEdges:
                if candEdges[e].dest == src and candEdges[e].source == dest: revEdge = e
                else:
                    if candEdges[e].dest == dest: candEdges[e].dest = newVert
                    if candEdges[e].dest == src: candEdges[e].dest = newVert
                    if candEdges[e].source == src: candEdges[e].source = newVert
                    if candEdges[e].source == dest: candEdges[e].source = newVert
            if revEdge != 0:
                del candEdges[revEdge]
            cand.edges = candEdges


        #TODO:
        ## update neighbor nodes to direct edges to new super node
        ## remove src and dest nodes from graph
        ## remove self edges from graph
        


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
        # randomly choose an edge to remove by flipping the associated allele to a 0
        e_key, e = random.choice(list(cand.edges.items()))
        cand.gene[e_key-1] = 0

        # create new graph reduction and check feasibility again
        edgesToRemove = []
        edgesToRemove.append(e_key)
        graphReduction(cand, edgesToRemove)
        feasibility(cand)

# This initializes the candidate population
def initializePop(vertices: dict[int, Vertex], edges: dict[int, Edge], edgeNodes: list[Vertex], targetNodes: list[Vertex]):
    geneLen = len(edges)
    candidatePopulation = []
    for _ in range(50):
        newCand = Candidate(geneLen)
        seedNum = random.randint(0, geneLen) / geneLen

        for i in range (geneLen):
            if (random.randint(0,100)/100) <= seedNum:
                newCand.gene[i] = 1

        newCand.vertices = vertices.copy()
        newCand.edges = edges.copy()

        edgesToRemove = []
        for a in range(len(newCand.gene)):
            if newCand.gene[a] == 0:
                edgesToRemove.append(a+1)
        graphReduction(newCand, edgesToRemove)
        repair(newCand)
        candidatePopulation.append(newCand)

    return candidatePopulation

def evaluate(pop: list[Candidate]):
    #TODO
    return

def selection(pop: list[Candidate]):
    #TODO
    return

def mutate(cand: Candidate):
    #TODO
    return cand

def crossover(pop: list[Candidate], vertices: dict[int, Vertex], edges: dict[int, Edge]):
    for _ in range(10):
        #TODO select parents
        #TODO cross parent's genes
        offspring = Candidate(len(edges))
        #TODO update offspring with information

        offspring = mutate(offspring)

        while offspring.feasible == False:
            repair(offspring, vertices, edges)
        pop.append(offspring)



# Main loop of the program
def main():
    # first up, initialize the graph file and pull relevant data out of .txt file
    (vertices, edgeNodes, targetNodes, edges) = initializeGraph()

    # now initialize the candidate population
    candidatePopulation = initializePop(vertices, edges, edgeNodes, targetNodes)

    # breed new generations of candidates
    for _ in range(50):
        candidatePopulation = evaluate(candidatePopulation)
        candidatePopulation = selection(candidatePopulation)
        candidatePopulation = crossover(candidatePopulation, vertices, edges)

    candidatePopulation = evaluate(candidatePopulation)
    fittestCand: Candidate = candidatePopulation.pop(0)
    print(fittestCand.gene)

    print("print statement for break point")

#main()

print("Finished Execution")