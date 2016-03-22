'''
Created on Dec 22, 2015

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.arnborg_proskurowski.reducible_feature import ReducibleFeature
from ivanov.graph.algorithms import r_ball_hyper, arnborg_proskurowski,\
    weisfeiler_lehman
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import nxext
from itertools import islice
import networkx as nx
import itertools
import sys

def extract_features(hypergraph, wl_iterations=0, wl_state=None):
    features = []
    
    for _, new_features, wl_state in extract_features_for_each_wl_iter(hypergraph, wl_iterations, wl_state):
        features += new_features
    
    return features, wl_state

def extract_features_for_each_wl_iter(hypergraph, wl_iterations=0, wl_state=None):
    raw_features = arnborg_proskurowski.get_reduced_features(hypergraph)
#     if tw == -1:
#         # TODO: How to handle graphs with larger tree-width?
#         # for now collect all possible features
#         print "The hypergraph has tree-width > 3."

    for i in range(wl_iterations + 1):
        if i == 1:
            hypergraph, wl_state = weisfeiler_lehman.init(hypergraph, wl_state)
        
        if i >= 1:
#             old_hypergraph = hypergraph
            hypergraph, wl_state = weisfeiler_lehman.iterate(hypergraph, wl_state, i)
        
        new_features = [process_raw_feature(raw_feature, hypergraph) for raw_feature in raw_features]
        
#         # NOTE: we should do all iterations, regardless if the graph is stable
#         if i >= 1:
#             # TODO: This way we extract features for the current WL iteration, although the labels may be stable
#             # This approach is good when all the labels are distinct, but if there was no refinement
#             # in the last WL iteration the extracted features will not be semantically different
#             # from the ones extracted in the previous iteration.
#             if weisfeiler_lehman.is_stable(old_hypergraph, hypergraph, i):
#                 break
    
        yield i, itertools.chain(*new_features), wl_state

def process_raw_feature(raw_feature, hypergraph, max_nodes=6):
    '''Turns a raw feature to a usable feature or a collection of features, depending on
    the type of the rule according to which the feature was reduced (fixed, pattern or dynamic).
    :param raw_feature: A ReducibleFeature extracted from Arnborg & Proskurowski
    :param hypergraph: A Hypergraph which contains the nodes of the raw feature.
    :param max_nodes: (default value 6) A number of nodes that a pattern or a dynamic feature can
    have before being disassembled in subfeatures of size max_nodes.
    :return A collection containing one or more features depending on the type of the raw feature.
    '''
    assert type(raw_feature) is ReducibleFeature
    assert type(hypergraph) is Hypergraph
    assert max_nodes > 3
    def get_feature_type(raw_feature):
        '''Get the type of the raw feature according to the rule it was reduced by.
        :param raw_feature: A ReducibleFeature.
        :return Type of the raw feature: 0 for "fixed", 1 for "pattern", 2 for "dynamic".
        '''
        rule = raw_feature.get_full_rule()
        if rule in ["2.1.0.0", "2.2.0.0", "4.2.0.0", "4.3.0.0", "5.2.3.1"]:
            return 1
        elif rule in ["5.2.2.0", "5.2.3.2", "5.2.4.0"]:
            return 2
        else:
            return 0
    
    def sliding_window(seq, window_size):
        # Returns a sliding window (of width window_size) over data from the iterable seq
        #   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
        it = iter(seq)
        result = tuple(islice(it, window_size))
        if len(result) == window_size:
            yield result
        for elem in it:
            result = result[1:] + (elem,)
            yield result
    
    feature_type = get_feature_type(raw_feature)
    if feature_type == 1:
        # pattern
        nodes_count = raw_feature.number_of_nodes()
        if nodes_count > max_nodes:
            rule = raw_feature.get_full_rule()
            if rule == "2.1.0.0":
                # chain: extract all subpaths of length max_nodes using a sliding window
                s = raw_feature.peripheral_nodes[0]
                t = raw_feature.peripheral_nodes[1]
                path = [s] + raw_feature.reducible_nodes + [t]
                for subpath in sliding_window(path, max_nodes):
                    yield hypergraph.subgraph_with_labels(set(subpath))
                raise StopIteration
            elif rule == "2.2.0.0":
                # ring: extract all subpaths of length max_nodes using a sliding window
                cycle = raw_feature.peripheral_nodes + raw_feature.reducible_nodes
                for subpath in sliding_window(cycle + cycle[:max_nodes - 1], max_nodes):
                    yield hypergraph.subgraph_with_labels(set(subpath))
                raise StopIteration
            elif rule == "4.2.0.0":
                # buddy: If there are more than 3 buddies create a buddy
                # configuration with 3 buddies for each possible combination
                assert len(raw_feature.peripheral_nodes) == 3
                buddy_nodes = raw_feature.reducible_nodes
                for buddy_nodes_subgroup in itertools.combinations(buddy_nodes, max_nodes - 3):
                    yield hypergraph.subgraph_with_labels(set(buddy_nodes_subgroup) | set(raw_feature.peripheral_nodes))
                raise StopIteration
            elif rule == "4.3.0.0":
                # cube: similar approach as for wheel (5.2.3.1)
                if nodes_count > max_nodes + 1:
                    reducible_neigh = [set(hypergraph.neighbors(node)) for node in raw_feature.reducible_nodes]
                    hub_node = reduce(lambda a, b: a.intersection(b), reducible_neigh)
                    ring_subgraph = hypergraph.subgraph(raw_feature.reducible_nodes | (raw_feature.peripheral_nodes - hub_node))
                    ring = nx.cycle_basis(ring_subgraph)
                    if len(ring) > 0:
                        ring = ring[0]
                        for subpath in sliding_window(ring + ring[:max_nodes - 1], max_nodes):
                            yield hypergraph.subgraph_with_labels(set(subpath) | hub_node)
                        raise StopIteration
                    else:
                        # if there is no ring in the feature, treat it as a fixed feature
                        # TODO: This can lead to a large number of shingles. Better solution?
                        pass
            elif rule == "5.2.3.1":
                # wheel: extract all cake-slice subpaths of length max_node using a sliding window
                if nodes_count > max_nodes + 1:
                    ring_subgraph = hypergraph.subgraph(raw_feature.reducible_nodes)
                    ring = nx.cycle_basis(ring_subgraph)
                    if len(ring) > 0:
                        ring = ring[0]
                        for subpath in sliding_window(ring + ring[:max_nodes - 1], max_nodes):
                            yield hypergraph.subgraph_with_labels(set(subpath) | set(raw_feature.peripheral_nodes))
                        raise StopIteration
                    else:
                        # if there is no ring in the feature, treat it as a fixed feature
                        # TODO: This can lead to a large number of shingles. Better solution?
                        pass
    elif feature_type == 2:
        # dynamic (the reducible nodes are always of degree 3):
        # for each pair of adjacent nodes u, v let a new feature be
        # the subgraph that contains u, v and all neighbors of u and v.
        nodes_count = raw_feature.number_of_nodes()
        if nodes_count > max_nodes:
            nodes = set(raw_feature.reducible_nodes) | set(raw_feature.peripheral_nodes)
            feature_graph = hypergraph.subgraph(nodes)
            adj_nodes = nxext.get_all_adjacent_nodes(feature_graph)
            neighbors = {node: nxext.get_all_neighbors(feature_graph, node) for node in nodes}
            for u, v in adj_nodes:
                node_subgroup = set([u, v] + neighbors[u] + neighbors[v])
                yield hypergraph.subgraph_with_labels(set(node_subgroup))
            raise StopIteration
    
    # fixed or pattern/dynamic with <= max_nodes number of nodes
    yield raw_feature.as_subgraph(hypergraph)

def get_feature_lists(graph_database, wl_iterations=0, iterator=True):
    def get_features_lists_generator():
        for record_id, element_hypergraphs, target in graph_database:
            # process the hypergraphs representing one element of the database
            features = []
            for hypergraph in element_hypergraphs:
                new_features, state["wl_state"] = extract_features(hypergraph, wl_iterations, state["wl_state"])
                features += new_features
            yield record_id, features, target
    
    state = {"wl_state": None}
    features_lists = get_features_lists_generator()
    
    if iterator:
        return features_lists
    else:
        features_lists = [(record_id, list(features), target) for record_id, features, target in features_lists]
        return features_lists, state["wl_state"]
