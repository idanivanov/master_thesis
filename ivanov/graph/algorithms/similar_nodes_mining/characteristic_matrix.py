'''
Created on Jan 13, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_nodes_mining import feature_extraction,\
    shingle_extraction, fingerprint
from ivanov.inout.serializable import Serializable

class CharacteristicMatrix(Serializable):
    
    @staticmethod
    def overestimate_time_to_build(nodes_count):
        '''Get the estimated time to build the characteristic matrix in seconds.
        '''
        ch_mat_per_node = 0.04
        time_for_ch_mat = nodes_count * ch_mat_per_node
        return time_for_ch_mat
    
    def build(self, feature_lists):
        self.sparse_matrix = {}
        i = -1
        for node, node_features in feature_lists:
            i += 1
            self.cols[node] = i # build node:column mapping
            for feature in node_features:
                shingles = shingle_extraction.extract_shingles(feature)
                fingerprints = fingerprint.get_fingerprints(shingles)
                for fp in fingerprints:
                    if not self.sparse_matrix.has_key(fp):
                        self.sparse_matrix[fp] = []
                    self.sparse_matrix[fp].append(i)
    
    def non_empty_rows(self):
        return self.sparse_matrix.keys()
    
    def __getitem__(self, key):
        return self.sparse_matrix[key]

    def __init__(self, hypergraph, r_in=0, r_out=0, r_all=0, wl_iterations=0):
        self.cols_count = hypergraph.number_of_nodes()
        self.cols = {}
        
        feature_lists = feature_extraction.get_feature_lists(hypergraph, r_in, r_out, r_all, wl_iterations)
        self.build(feature_lists)
