'''
Created on Dec 22, 2015

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.arnborg_proskurowski.reducible_feature import ReducibleFeature
from ivanov.graph.algorithms import r_ball_hyper, arnborg_proskurowski,\
    weisfeiler_lehman
from ivanov.graph.hypergraph import Hypergraph
from itertools import islice
import networkx as nx
import itertools
import sys

def extract_features(node, hypergraph, r_in=0, r_out=0, r_all=0, wl_iterations=0, wl_labels_list = []):
    rballs = {"in": r_ball_hyper(hypergraph, node, r_in, edge_dir=-1) if r_in > 0 else None,
              "out": r_ball_hyper(hypergraph, node, r_out, edge_dir=1) if r_out > 0 else None,
              "all": r_ball_hyper(hypergraph, node, r_all, edge_dir=0) if r_all > 0 else None}
    
    features = []
    
    if wl_iterations > 0:
        new_wl_labels_list = list(wl_labels_list)
    else:
        new_wl_labels_list = []
    
    for key in rballs:
        rball = rballs[key]
        if rball is None:
            continue
        
        raw_features = arnborg_proskurowski.get_reduced_features(rball)
#         if tw == -1:
#             # TODO: How to handle graphs with larger tree-width?
#             # for now collect all possible features
#             print "The {0}-rball of node {1} has tree-width > 3.".format(key, node)

        for i in range(wl_iterations + 1):
            if i == 1:
                rball, new_wl_labels_list = weisfeiler_lehman.init(rball, new_wl_labels_list)
            
            if i >= 1:
                new_rball, new_wl_labels_list = weisfeiler_lehman.iterate(rball, new_wl_labels_list)
                # TODO: should we skip the stability check for the first iteration?
#                 if i > 1 and weisfeiler_lehman.is_stable(rball, new_rball, i):
                if weisfeiler_lehman.is_stable(rball, new_rball, i):
                    break
                rball = new_rball
            
            new_features = [process_raw_feature(raw_feature, rball) for raw_feature in raw_features]
            features += itertools.chain(*new_features)
    
    return features, new_wl_labels_list

def process_raw_feature(raw_feature, rball, max_nodes=6):
    '''Turns a raw feature to a usable feature or a collection of features, depending on
    the type of the rule according to which the feature was reduced (fixed, pattern or dynamic).
    :param raw_feature: A ReducibleFeature extracted from Arnborg & Proskurowski
    :param rball: A Hypergraph which contains the nodes of the raw feature.
    :param max_nodes: (default value 6) A number of nodes that a pattern or a dynamic feature can
    have before being disassembled in subfeatures of size max_nodes.
    :return A collection containing one or more features depending on the type of the raw feature.
    '''
    assert type(raw_feature) is ReducibleFeature
    assert type(rball) is Hypergraph
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
        "Returns a sliding window (of width window_size) over data from the iterable seq"
        "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
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
                    yield rball.subgraph_with_labels(subpath)
                raise StopIteration
            elif rule == "2.2.0.0":
                # ring: extract all subpaths of length max_nodes using a sliding window
                cycle = raw_feature.peripheral_nodes + raw_feature.reducible_nodes
                for subpath in sliding_window(cycle + cycle[:max_nodes - 1], max_nodes):
                    yield rball.subgraph_with_labels(subpath)
                raise StopIteration
            elif rule == "4.2.0.0":
                # buddy: If there are more than 3 buddies create a buddy
                # configuration with 3 buddies for each possible combination
                assert len(raw_feature.peripheral_nodes) == 3
                buddy_nodes = raw_feature.reducible_nodes
                for buddy_nodes_subgroup in itertools.combinations(buddy_nodes, max_nodes - 3):
                    yield rball.subgraph_with_labels(buddy_nodes_subgroup + list(raw_feature.peripheral_nodes))
                raise StopIteration
            elif rule == "4.3.0.0":
                # cube: similar approach as for wheel (5.2.3.1)
                reducible_neigh = [set(rball.neighbors(node)) for node in raw_feature.reducible_nodes]
                hub_node = reduce(lambda a, b: a.intersection(b), reducible_neigh)
                ring_subgraph = rball.subgraph(raw_feature.reducible_nodes | (raw_feature.peripheral_nodes - hub_node))
                ring = nx.cycle_basis(ring_subgraph)[0]
                hub_node = list(hub_node)
                for subpath in sliding_window(ring + ring[:max_nodes - 1], max_nodes):
                    yield rball.subgraph_with_labels(subpath + hub_node)
                raise StopIteration
            elif rule == "5.2.3.1":
                # wheel: extract all cake-slice subpaths of length max_node using a sliding window
                ring_subgraph = rball.subgraph(raw_feature.reducible_nodes)
                ring = nx.cycle_basis(ring_subgraph)[0]
                for subpath in sliding_window(ring + ring[:max_nodes - 1], max_nodes):
                    yield rball.subgraph_with_labels(subpath + list(raw_feature.peripheral_nodes))
                raise StopIteration
    elif feature_type == 2:
        # dynamic
        nodes_count = raw_feature.number_of_nodes()
        if nodes_count > max_nodes:
            nodes = set(raw_feature.reducible_nodes) | set(raw_feature.peripheral_nodes)
            node_subgroups = itertools.combinations(nodes, max_nodes)
            for node_subgroup in node_subgroups:
                yield rball.subgraph_with_labels(node_subgroup)
            raise StopIteration
    
    # fixed or pattern/dynamic with <= max_nodes number of nodes
    yield raw_feature.as_subgraph(rball)

def get_feature_lists(hypergraph, r_in=0, r_out=0, r_all=0, wl_iterations=0):
    assert type(hypergraph) is Hypergraph
    wl_labels_lists = []
    for node in hypergraph.nodes_iter():
        features, wl_labels_lists = extract_features(node, hypergraph, r_in, r_out, r_all, wl_iterations, wl_labels_lists) 
        yield node, features
