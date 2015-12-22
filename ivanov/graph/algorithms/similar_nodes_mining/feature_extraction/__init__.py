'''
Created on Dec 22, 2015

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms import r_ball_hyper, arnborg_proskurowski,\
    weisfeiler_lehman
import sys

def extract_features(node, hypergraph, r_in=0, r_out=0, r_all=0, wl_iterations=0, wl_labels_lists = [[]]):
    rballs = {"in": r_ball_hyper(hypergraph, node, r_in, edge_dir=-1) if r_in > 0 else None,
              "out": r_ball_hyper(hypergraph, node, r_out, edge_dir=1) if r_out > 0 else None,
              "all": r_ball_hyper(hypergraph, node, r_all, edge_dir=0) if r_all > 0 else None}
    
    features = []
    
    for key in rballs:
        rball = rballs[key]
        if rball is None:
            continue
        
        for i in range(wl_iterations + 1):
            if i == 1:
                new_wl_labels_lists = list(wl_labels_lists)
                rball, new_wl_labels_lists[0] = weisfeiler_lehman.init(rball, wl_labels_lists[0])
            
            if i > 1:
                if len(new_wl_labels_lists) < i:
                    wl_labels_lists.append([])
                rball, new_wl_labels_lists[i] = weisfeiler_lehman.iteration(rball, new_wl_labels_lists[i])
            
            canon_str, new_raw_features = arnborg_proskurowski.get_canonical_representation(rball, True)
            features += map(lambda raw_feature: raw_feature.as_subgraph(rball), new_raw_features)
            if canon_str == u"Tree-width > 3":
                # TODO: How to handle graphs with larger tree-width?
                # for now collect all possible features
                sys.stderr.write("\n[feature_extraction] Cannot extract features because the r-ball has tree-width > 3.\n")
    
    return features, new_wl_labels_lists

def get_feature_lists(hypergraph, r_in=0, r_out=0, r_all=0, wl_iterations=0):
    wl_labels_lists = []
    for node in hypergraph.nodes_iter():
        features, wl_labels_lists = extract_features(node, hypergraph, r_in, r_out, r_all, wl_iterations, wl_labels_lists) 
        yield node, features
