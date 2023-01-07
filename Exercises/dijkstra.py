from collections import defaultdict


class Graph:
    def __init__(self):
        self.nodes = set()  # A set cannot contain duplicate nodes
        self.neighbours = defaultdict(
            list)  # Defaultdict is a child class of Dictionary that provides a default value for a key that does not exists.
        self.distances = {}  # Dictionary. An example record as ('A', 'B'): 6 shows the distance between 'A' to 'B' is 6 units

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self.neighbours[from_node].append(to_node)
        self.neighbours[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance
        self.distances[(to_node, from_node)] = distance  # lets make the graph undirected / bidirectional

    def print_graph(self):
        print("Set of Nodes are: ", self.nodes)
        print("Neighbours are: ", self.neighbours)
        print("Distances are: ", self.distances)

def dijkstra(graph, source):
    # Declare and initialize result, unvisited, and path
    unvisited = set(graph.nodes)
    result = {source: 0}
    path = dict()
    # As long as unvisited is non-empty
    curr_node = source
    while unvisited:
        # 1. Find the unvisited node having smallest known distance from the source node.
        potential_nodes = {k: v for k, v in result.items() if k in unvisited}
        sorted_nodes = sorted(list(potential_nodes.items()), key=lambda x: x[1])
        curr_node = sorted_nodes[0][0]
        # 2. For the current node, find all the unvisited neighbours. For this, you have calculate the distance of each unvisited neighbour.
        neighbours = [n for n in graph.neighbours[curr_node] if n in unvisited]
        # 3. If the calculated distance of the unvisited neighbour is less than the already known distance in result dictionary, update the shortest distance in the result dictionary.
        # 4. If there is an update in the result dictionary, you need to update the path dictionary as well for the same key.
        for n in neighbours:
            cost = graph.distances[(curr_node, n)] + result.get(curr_node, 0)
            if n not in result or cost < result[n]:
                result[n] = cost
                path[n] = curr_node
        # 5. Remove the current node from the unvisited set.
        unvisited.remove(curr_node)
    return result


if __name__ == "__main__":
    # Test 1
    testGraph = Graph()
    for node in ['A', 'B', 'C', 'D', 'E']:
        testGraph.add_node(node)

    testGraph.add_edge('A', 'B', 3)
    testGraph.add_edge('A', 'D', 2)
    testGraph.add_edge('B', 'D', 4)
    testGraph.add_edge('B', 'E', 6)
    testGraph.add_edge('B', 'C', 1)
    testGraph.add_edge('C', 'E', 2)
    testGraph.add_edge('E', 'D', 1)

    assert dijkstra(testGraph, 'A') == {'A': 0, 'D': 2, 'B': 3, 'E': 3, 'C': 4}

    graph = Graph()
    for node in ['A', 'B', 'C']:
        graph.add_node(node)

    graph.add_edge('A', 'B', 5)
    graph.add_edge('B', 'C', 5)
    graph.add_edge('A', 'C', 10)

    assert dijkstra(graph, 'A') == {'A': 0, 'C': 10, 'B': 5}

    graph = Graph()
    for node in ['A', 'B', 'C', 'D', 'E', 'F']:
        graph.add_node(node)

    graph.add_edge('A', 'B', 5)
    graph.add_edge('A', 'C', 4)
    graph.add_edge('D', 'C', 1)
    graph.add_edge('B', 'C', 2)
    graph.add_edge('A', 'D', 2)
    graph.add_edge('B', 'F', 2)
    graph.add_edge('C', 'F', 3)
    graph.add_edge('E', 'F', 2)
    graph.add_edge('C', 'E', 1)

    assert dijkstra(graph, 'A') == {'A': 0, 'C': 3, 'B': 5, 'E': 4, 'D': 2, 'F': 6}