# Tabu Search to solve the sensor placement problem
# Written by: Joshua Rinaldi
# For: AFIT/ENG CSCE 686, Spring 2021 Final Project

import random
from copy import deepcopy

class Neighbor(object):
    #TODO define
    def __init__(self, geneLen):
        self.gene = []
        for _ in range(geneLen):
            self.gene.append(0)
        self.vertices = dict[int, Vertex]
        self.edges = dict[int, Edge]
        self.fitness

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

def initializeGraph():
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

def generateSeed(vertices: dict[int, Vertex], edges: dict[int, Edge]):
    #TODO implement
    return

def generateNeighbors(curSol: Neighbor, vertices: dict[int, Vertex], edges: dict[int, Edge]):
    #TODO implement
    return


def main():
    (vertices, edgeNodes, targetNodes, edges) = initializeGraph()

    curSol = generateSeed(vertices, edges)
    
    noImprovement = False
    split = False
    noImprovementIdx = 0
    tabuList: dict[Neighbor, int]
    curFittest = curSol

    while noImprovementIdx < 10 and split == False:
        neighborhood = generateNeighbors(curSol, vertices, edges)
        nextSol = neighborhood.pop(0)
        while nextSol in tabuList:
            nextSol = neighborhood.pop(0)
        if nextSol.fitness > curFittest.fittest:
            curFittest = nextSol
            noImprovementIdx = -1
        #TODO update tabu list
        curSol = nextSol
        if len(curSol.vertices) == 2:
            split = True
        noImprovementIdx += 1
        if noImprovementIdx >= 10:
            noImprovement = True



main()

print("Finished Execution")