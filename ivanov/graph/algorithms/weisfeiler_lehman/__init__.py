'''
Created on Oct 5, 2015

@author: Ivan Ivanov
'''

import networkx as nx
from ivanov.graph import nxext
from ivanov.graph.hypergraph import Hypergraph

def iterate(graph, labels_list):
    '''Performs one iteration of the Weisfeiler-Lehman algorithm.
    :param graph: A Networkx graph or a Hypergraph
    :param labels_list: A list of labels. Each label is uniquely
    identified by its position index in the list.
    :param iteration: The current iteration number.
    :return A tuple of the form (new_graph, new_labels_list), where
    new_graph is the resulting graph from the iteration, new_labels_list
    is the new list of labels for the current iteration of the algorithm.
    '''
    
    def get_new_label(node, neighbors):
        node_label = graph.node[node]["labels"][0]
        label_extensions = []
        
        for neighbor in neighbors:
            neighbor_label = graph.node[neighbor]["labels"][0]
            label_extensions.append(neighbor_label)
        
        label_extensions.sort()
        
        return "{0};{1}".format(node_label, ",".join(label_extensions))
    
    new_graph = graph.copy()
    new_labels_list = []
    new_node_labels = {}
    
    labels_set = set(labels_list)
    new_labels_set = set()
    
    for node in graph.node:
        if type(graph) is not Hypergraph:
            neighbors = nxext.get_all_neighbors(graph, node)
        else:
            neighbors = graph.bipartite_graph.neighbors(node)
        new_node_label = get_new_label(node, neighbors)
        if new_node_label not in new_labels_set and new_node_label not in labels_set:
                new_labels_list.append(new_node_label)
                new_labels_set.add(new_node_label)
        new_node_labels[node] = new_node_label
    
    new_labels_list.sort()
    new_labels_list = labels_list + new_labels_list
    
    for node in graph.node:
        new_graph.node[node]["labels"] = [str(new_labels_list.index(new_node_labels[node]))]
    
    return new_graph, new_labels_list
    
def init(graph, labels_list = []):
    '''Initialize the graph for performing Weisfeiler-Lehman algorithm.
    :param graph: Can be a Networkx graph or a Hypergraph.
    :param labels_list: Optional. A list of predefined labels, whose
    indices in the list will be used as indices of their occurrences
    in the next iterations of the algorithm.
    '''
    def init_labels(_graph):
        for node in _graph.node:
            if "labels" not in _graph.node[node]:
                _graph.node[node]["labels"] = ["0"]
            elif not _graph.node[node]["labels"]:
                _graph.node[node]["labels"] = ["0"]
            elif len(_graph.node[node]["labels"]) != 1:
                labels = _graph.node[node]["labels"]
                labels.sort()
                joined = ",".join(labels)
                _graph.node[node]["labels"] = [joined]
    
    new_graph = graph.copy()
    init_labels(new_graph)
    
    # the labels in this list are represented by their indices in the new labels
    new_labels_list = []
    new_labels_set = set()
    labels_set = set(labels_list)
    
    for node in graph.node:
        node_label = new_graph.node[node]["labels"][0]
        if node_label not in labels_set and node_label not in new_labels_set:
            new_labels_list.append(node_label)
            new_labels_set.add(node_label)
    
    new_labels_list.sort()
    new_labels_list = labels_list + new_labels_list
    
    for node in graph.node:
        old_label = new_graph.node[node]["labels"][0]
        new_graph.node[node]["labels"] = [str(new_labels_list.index(old_label))]
    
    return new_graph, new_labels_list
    
# TODO: what do we do when all labels are different?
def is_stable(graph, new_graph, iteration=0):
    is_stable = True
    
    if type(graph) is not Hypergraph:
        nodes_count = graph.number_of_nodes()
    else:
        nodes_count = graph.bipartite_graph.number_of_nodes()
    
    if iteration > nodes_count:
        return True
    
    for node_1 in graph.node:
        node_1_label = graph.node[node_1]["labels"][0]
        node_1_new_label = new_graph.node[node_1]["labels"][0]
        for node_2 in graph.node:
            if node_1 != node_2:
                node_2_label = graph.node[node_2]["labels"][0]
                node_2_new_label = new_graph.node[node_2]["labels"][0]
                if node_1_label == node_2_label or node_1_new_label == node_2_new_label:
                    if node_1_label == node_2_label and node_1_new_label == node_2_new_label:
                        continue
                    else:
                        is_stable = False
                        break
    
    return is_stable
