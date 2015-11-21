'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

import networkx as nx
from itertools import chain, combinations
import matplotlib.pyplot as plt
from unidecode import unidecode


def Graph(directed=False, multigraph=False):
    if directed:
        if multigraph:
            return nx.MultiDiGraph()
        else:
            return nx.DiGraph()
    else:
        if multigraph:
            return nx.MultiGraph()
        else:
            return nx.Graph()

def get_all_adjacent_nodes(graph):
    return set(map(lambda pair: tuple(sorted(list(pair))), graph.edges_iter()))

def has_any_edge(graph, u, v):
    if graph.has_edge(u, v) or graph.has_edge(v, u):
        return True
    else:
        return False

def get_all_neighbors(graph, node):
    neighbors = graph.neighbors(node)
    if graph.is_directed():
        neighbors += graph.predecessors(node)
    return list(set(neighbors))

def get_edge_labels_raw(graph, u, v):
    edges = []
    if graph.has_edge(u, v):
        edges_dict = graph.edge[u][v]
        if graph.is_multigraph():
            edges = [edges_dict[edge]["label"] for edge in edges_dict]
        else:
            edges = [edges_dict["label"]]
    return edges

def get_edges(graph, u, v):
    edges = []
    if graph.has_edge(u, v):
        if graph.is_multigraph():
            edges = [(u, v) for _ in graph.edge[u][v]]
        else:
            edges = [(u, v)]
    return edges

def get_self_loops(graph):
    return filter(lambda edge: edge[0] == edge[1], graph.edges_iter())

def get_edge_labels_and_dirs(graph, u, v):
    labels_and_dirs = []
    edges_u_to_v = get_edge_labels_raw(graph, u, v)
    edges_v_to_u = get_edge_labels_raw(graph, v, u)
    for edge_label in edges_u_to_v:
        if edge_label in edges_v_to_u:
            labels_and_dirs.append((edge_label, 0))
            edges_v_to_u.remove(edge_label)
        else:
            labels_and_dirs.append((edge_label, 1))
    for edge_label in edges_v_to_u:
        labels_and_dirs.append((edge_label, -1))
    return labels_and_dirs

def visualize_graph(graph, node_labels = True, edge_labels = True, bipartite = False, save_to_file = None, font_size = 10):
    def all_labels_to_ascii(graph):
        new_graph = graph.copy()
        for node in new_graph.nodes_iter():
            label = graph.node[node]["labels"][0]
            if len(label) > 100:
                new_label = "long_string"
            else:
                new_label = unidecode(label)
            new_graph.node[node]["labels"] = [new_label]
        # if necessary, convert edge labels too
        return new_graph
    new_graph = all_labels_to_ascii(graph)
    pos = nx.graphviz_layout(new_graph)
    fig, ax = plt.subplots()
    if bipartite:
        part_1 = filter(lambda node: new_graph.node[node]["bipartite"] == 0, new_graph.nodes_iter())
        part_2 = filter(lambda node: new_graph.node[node]["bipartite"] == 1, new_graph.nodes_iter())
        nx.draw_networkx_nodes(new_graph, pos, ax=ax, nodelist=part_1, node_color="r")
        nx.draw_networkx_nodes(new_graph, pos, ax=ax, nodelist=part_2, node_color="b")
        nx.draw_networkx_edges(new_graph, pos, ax=ax, edgelist=new_graph.edges())
    else:
        nx.draw(new_graph, pos, ax=ax)
    if node_labels:
        labels = {node: ",".join(new_graph.node[node]["labels"]) for node in new_graph.nodes_iter()}
#         labels = {node: node for node in new_graph.nodes_iter()}
        nx.draw_networkx_labels(new_graph, pos, labels=labels, ax=ax, font_size=font_size)
    if edge_labels:
        if new_graph.is_multigraph():
            edge_labels = {edge: new_graph.edge[edge[0]][edge[1]][0]["label"] for edge in new_graph.edges_iter()}
        else:
            edge_labels = {edge: new_graph.edge[edge[0]][edge[1]]["label"] for edge in new_graph.edges_iter()}
        nx.draw_networkx_edge_labels(new_graph, pos, edge_labels=edge_labels, ax=ax)
    plt.axis('off')
    plt.show()
    if save_to_file:
        fig.savefig(save_to_file, format="eps")
