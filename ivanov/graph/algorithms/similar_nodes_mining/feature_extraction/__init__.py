'''
Created on Dec 22, 2015

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms import r_ball_hyper, arnborg_proskurowski,\
    weisfeiler_lehman
from ivanov.graph.hypergraph import Hypergraph
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
            
            features += [raw_feature.as_subgraph(rball) for raw_feature in raw_features]
    
    return features, new_wl_labels_list

def get_feature_lists(hypergraph, r_in=0, r_out=0, r_all=0, wl_iterations=0):
    assert type(hypergraph) is Hypergraph
    wl_labels_lists = []
    for node in hypergraph.nodes_iter():
        features, wl_labels_lists = extract_features(node, hypergraph, r_in, r_out, r_all, wl_iterations, wl_labels_lists) 
        yield node, features
