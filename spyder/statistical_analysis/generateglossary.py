import networkx as nx
import pickle
import re

# load the graph, graph.pickle
with open('graph.pickle', 'rb') as f:
    G = pickle.load(f)

# load the glossary.csv
with open('glossary.csv', 'r') as f:
    glossary = f.readlines()

def get_top_nodes(node_name, n=2):
    # get the node
    node = G.nodes[node_name]
    # get the edges
    edges = G.edges(node_name, data=True)
    # get the top 5 connected nodes based on the pagerank of the in nodes
    top_nodes = sorted([(u, G.nodes[u]['pagerank']) for _, u, _ in edges], key=lambda x: x[1], reverse=True)
    # top nodes with name.split(' ')==n
    top_nodes = [u for u, _ in top_nodes if len(u.split(' '))==n][:30]
    # return the top 5 connected nodes
    return top_nodes

# create a dictionary of the glossary
glossary_dict = {}
for line in glossary:
    line = line.lower()
    # remove punctuation of all kinds
    line = re.sub(r'[^\w\s]','',line)
    # remove new line characters '\n'
    line = line.replace('\n','')
    glossary_dict[line[0]] = True

for term in glossary:
    term = term.lower()
    # remove punctuation of all kinds
    term = re.sub(r'[^\w\s]','',term)
    # remove new line characters '\n'
    term = term.replace('\n','')

    # get the top 30 connected nodes for n=2 to n=4
    top_nodes = []
    for n in range(2,5):
        try:
            top_nodes += get_top_nodes(term, n=n)
        except:
            pass
        
    # iterate through the top nodes and prompt user to add to glossary
    for node in top_nodes:
        if node not in glossary_dict:
            print('Add {} to glossary?'.format(node))
            response = input()
            if response.lower() == 'y':
                glossary_dict[node] = True
                print('Added {} to glossary'.format(node))

# update the glossary.csv
with open('glossary.csv', 'w') as f:
    for term in glossary_dict.keys():
        f.write(term+'\n')