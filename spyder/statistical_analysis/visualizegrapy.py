import networkx
import pyvis
import pickle

def visualize_graph(G):
    # create a pyvis network object
    pv = pyvis.network.Network()

    # add nodes and edges to the pyvis network object
    for node in G.nodes:
        pv.add_node(node, size=G.nodes[node]['pagerank']*10)

    for u, v in G.edges:
        pv.add_edge(u, v, weight=G.edges[u, v]['weight'])

    # return and also save
    return pv.show('graph.html')

def load_graph(filename):
    """
    Load a graph from a pickle file
    """
    with open(filename, 'rb') as f:
        graph = pickle.load(f)
    # select random subset of nodes
    nodes = list(graph.nodes)
    nodes = nodes[:100]
    graph = graph.subgraph(nodes)
    return graph

def main():
    """
    Main function
    """
    graph = load_graph('graph.pickle')
    visualize_graph(graph)

if __name__ == '__main__':
    main()