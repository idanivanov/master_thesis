'''
Created on Dec 22, 2015

@author: Ivan Ivanov
'''

def extract_features(hypergraph, node):
    return set() # TODO: implement feature extraction

def get_feature_lists(hypergraph):
    for node in hypergraph.nodes_iter():
        yield node, extract_features(hypergraph, node)