import networkx as nx
import pickle
import re
import tqdm

# load the graph, graph.pickle
with open('graph.pickle', 'rb') as f:
    G = pickle.load(f)

# load the blog topics
with open('blogtopics.csv', 'r') as f:
    # pre process the topics
    topics = [re.sub(r'[^a-zA-Z0-9 ]', '', line.strip().lower()) for line in f.readlines()]

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

# for each topic, get the top 15 connected nodes with n=2 to n=4
related_keywords = dict()
for topic in tqdm.tqdm(topics):
    related_keywords[topic] = list()
    for n in range(2, 5):
        try:
            related_keywords[topic] += get_top_nodes(topic, n)
        except:
            pass

# save the related keywords into a csv file: topic, keywords separated by ';'
with open('relatedkeywords.csv', 'w') as f:
    for topic in topics:
        f.write(topic + ',' + ';'.join(related_keywords[topic]) + '\n')