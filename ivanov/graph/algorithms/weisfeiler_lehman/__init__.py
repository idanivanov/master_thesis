'''
Created on Oct 5, 2015

@author: Ivan Ivanov
'''

import networkx as nx
from ivanov.graph import nxext
from ivanov.graph.hypergraph import Hypergraph

def iterate(graph, wl_state, iteration, test_mode=False):
    '''Performs one iteration of the Weisfeiler-Lehman algorithm.
    :param graph: A Networkx graph or a Hypergraph
    :param wl_state: A dictionary containing 2 sub-dictionaries:
    "labels" contains a mapping from the full original graph labels or
    labels generated during the Weisfeiler & Lehman iterations to their
    corresponding WL short unique labels; "next_labels" contains the next label
    number for each WL iteration.
    :param iteration: The current iteration number.
    :return A tuple of the form (new_graph, new_labels_list), where
    new_graph is the resulting graph from the iteration, new_labels_list
    is the new list of labels for the current iteration of the algorithm.
    '''
    def get_new_label(node, neighbors):
        def get_direction(u, v):
            '''Get the direction of the edge between nodes u and v
            '''
            res = 0
            if type(graph) is not Hypergraph:
                if graph.has_edge(u, v) and graph.has_edge(v, u):
                    res = 0
                elif graph.has_edge(u, v):
                    res = 1
                elif graph.has_edge(v, u):
                    res = -1
                else:
                    raise Exception("There is no edge between {0} and {1}.".format(u, v))
            else:
                if u.startswith(u"e_"):
                    # u represents an edge -> all the neighbors are nodes
                    n = v
                    e = u
                    k = -1
                else:
                    # u represents a node -> all the neighbors are edges
                    n = u
                    e = v
                    k = 1
                dir_perms = graph.node[e]["direction"]
                dir_perm_0 = next(iter(dir_perms))
                if len(dir_perm_0) > 2:
                    raise Exception("Weisfeiler-Lehman is not implemented for hypergraphs with edges of order > 2.")
                if len(dir_perms) != 1:
                    res = 0
                elif dir_perm_0.index(n) == 0:
                    res = k
                elif dir_perm_0.index(n) == 1:
                    res = -k
                else:
                    raise Exception("Strange direction encoding of an edge. Are {0} and {1} connected?".format(u, v))
            return "out" if res > 0 else "in" if res < 0 else "any"
        
        node_label = graph.node[node]["labels"][0]
        label_extensions = {"any" : [], "in" : [], "out" : []}
        
        for neighbor in neighbors:
            neighbor_label = graph.node[neighbor]["labels"][0]
            direction = get_direction(node, neighbor)
            label_extensions[direction].append(neighbor_label)
        
        label_extension = []
        for direction in ["any", "in", "out"]:
            if label_extensions[direction]:
                label_extensions[direction].sort()
                label_extension.append("{0}({1})".format(direction, ",".join(label_extensions[direction])))
        label_extension = ",".join(label_extension)
        
        return "{0};{1}".format(node_label, label_extension)
    
    new_graph = graph.copy()
    
    if iteration not in wl_state["next_labels"]:
        wl_state["next_labels"][iteration] = 0
    
    if test_mode:
        nodes = sorted(graph.node, key=lambda n: graph.node[n]["labels"][0])
    else:
        nodes = graph.node
    
    for node in nodes:
        if type(graph) is not Hypergraph:
            neighbors = nxext.get_all_neighbors(graph, node)
        else:
            neighbors = graph.bipartite_graph.neighbors(node)
        new_node_label = get_new_label(node, neighbors)
        if new_node_label not in wl_state["labels"]:
                wl_state["labels"][new_node_label] = "wl_{0}.{1}".format(iteration, wl_state["next_labels"][iteration])
                wl_state["next_labels"][iteration] += 1
        new_graph.node[node]["labels"] = [wl_state["labels"][new_node_label]]
    
    return new_graph, wl_state
    
def init(graph, wl_state=None, test_mode=False):
    '''Initialize the graph for performing Weisfeiler-Lehman algorithm.
    :param graph: Can be a Networkx graph or a Hypergraph.
    :param wl_state: Optional. A dictionary containing 2 sub-dictionaries:
    "labels" contains a mapping from the full original graph labels or
    labels generated during the Weisfeiler & Lehman iterations to their
    corresponding WL short unique labels; "next_labels" contains the next label
    number for each WL iteration.
    '''
#     def init_labels(_graph):
#         # TODO: This function is not really necessary
#         for node in _graph.node:
#             if "labels" not in _graph.node[node]:
#                 _graph.node[node]["labels"] = ["0"]
#             elif not _graph.node[node]["labels"]:
#                 _graph.node[node]["labels"] = ["0"]
#             elif len(_graph.node[node]["labels"]) != 1:
#                 labels = _graph.node[node]["labels"]
#                 labels.sort()
#                 joined = ",".join(labels)
#                 _graph.node[node]["labels"] = [joined]
    
    new_graph = graph.copy()
#     init_labels(new_graph)
    
    if wl_state is None:
        wl_state = {
            "labels": {},
            "next_labels": {0: 0}
        }
    
    if test_mode:
        nodes = sorted(graph.node, key=lambda n: graph.node[n]["labels"][0])
    else:
        nodes = graph.node
    
    for node in nodes:
        node_label = new_graph.node[node]["labels"][0]
        if node_label not in wl_state["labels"]:
            wl_state["labels"][node_label] = "wl_0.{0}".format(wl_state["next_labels"][0])
            wl_state["next_labels"][0] += 1
        new_graph.node[node]["labels"] = [wl_state["labels"][node_label]]
    
    return new_graph, wl_state
    
# TODO: what do we do when all labels are different?
def is_stable(graph, new_graph, iteration=0):
    is_stable = True
    
    if type(graph) is not Hypergraph:
        nodes_count = graph.number_of_nodes()
    else:
        nodes_count = graph.bipartite_graph.number_of_nodes()
    
    if iteration > nodes_count:
        return True
    
    repeating_new_labels = False
    
    for node_1 in graph.node:
        node_1_label = graph.node[node_1]["labels"][0]
        node_1_new_label = new_graph.node[node_1]["labels"][0]
        for node_2 in graph.node:
            if node_1 != node_2:
                node_2_label = graph.node[node_2]["labels"][0]
                node_2_new_label = new_graph.node[node_2]["labels"][0]
                old_labels_cond = node_1_label == node_2_label
                new_labels_cond = node_1_new_label == node_2_new_label
                if old_labels_cond or new_labels_cond:
                    if old_labels_cond and new_labels_cond:
                        repeating_new_labels = True
                        continue
                    else:
                        is_stable = False
                        if repeating_new_labels:
                            break
    
    if not is_stable and not repeating_new_labels:
        # There is nothing to refine, since each new label appears only once in the graph
        is_stable = True
    
    return is_stable
