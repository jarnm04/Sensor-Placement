# This file will generate a random graph based upon the parameters provided by a user
# The graph generated will be store in a .txt file in a format useable by the various scripts
# This script will operate under the assumption that a taret node is not allowed to be an edge
# node, while this may not be the case for seom networks, it is assumed here

import random

numNodes = input("Number of nodes in network: ")
numNodes = int(numNodes)

numEdges = input("Number of edge nodes: ")
numEdges = int(numEdges)

numTargets = input("Number of targets: ")
numTargets = int(numTargets)

fileName = input("Output file name: ")

targetNodes = []
edgeNodes = []

for i in range(numTargets):
    node = random.randint(1, numNodes)
    while (node in targetNodes) == True:
        node = random.randint(1, numNodes)
    targetNodes.append(node)

for i in range(numEdges):
    node = random.randint(1, numNodes)
    while (node in edgeNodes) == True or (node in targetNodes) == True:
        node = random.randint(1, numNodes)
    edgeNodes.append(node)

with open("{}".format(fileName), "w") as file:
    for i in range (1, numNodes+1):
        # add node name to file
        file.write("{}\n".format(i))

        # add whether node is target, edge or neither
        if i in targetNodes:
            file.write("T\n")
        elif i in edgeNodes:
            file.write("E\n")
        else:
            file.write("N\n")
        
        # add number of vulnerabilities on node
        numVuln = random.randint(1, 15)
        file.write("{}\n".format(numVuln))

        # add number of neighbors
        numNeighbors = random.randint(1, numNodes)
        neighbors = []
        file.write("{}\n".format(numNeighbors))

        # add neighbors
        for j in range(numNeighbors):
            newNeighbor = random.randint(1,numNodes)
            while newNeighbor in neighbors:
                newNeighbor = random.randint(1,numNodes)
            neighbors.append(newNeighbor)
            file.write("{}\n".format(newNeighbor))
        file.write("#\n")