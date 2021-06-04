# This is the deterministic approach to solving the sensor placement problem

# Object class for the vertex
class Vertex(object):
    def __init__(self, name, numVulns, neighbors, type, numNeighbors ):
        self.name = name
        self.numVulns = numVulns
        self.neighbors = neighbors
        self.type = type

# This will read through the file until it hits a stopping character, creating a new vertex
def makeVertex(file_lines):
    name = file_lines.pop(0)
    name = int(name)
    type = file_lines.pop(0)
    numVulns = file_lines.pop(0)
    numNeighbors = file_lines.pop(0)
    neighbors = []
    while file_lines[0] != "#":
        n = file_lines.pop(0)
        n = int(n)
        neighbors.append(n)
    file_lines.pop(0)
    newVertex = Vertex(name, numVulns, neighbors, type, numNeighbors)

    return newVertex


# Initialization function. It will ingest a user indicated file and return that as a useable
# array of vertices in the graph
def initializeGraph():
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

    return (vertices, edgeNodes, targetNodes)







def main():
    (vertices, edgeNodes, targetNodes) = initializeGraph()
    print("Finished!")

main()