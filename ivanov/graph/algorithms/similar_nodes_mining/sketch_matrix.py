'''
Created on Dec 21, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_nodes_mining import feature_extraction,\
    fingerprint, shingle_extraction
from ivanov.graph.algorithms.similar_nodes_mining.min_hash_function import MinHashFunction
import cPickle as pickle
import numpy as np
import contextlib
import gzip

class SketchMatrix(object):
    def build_sketch_matrix(self, feature_lists):
        def build_characteristic_matrix(feature_lists):
            ch_mat = {}
            i = -1
            for node, node_features in feature_lists:
                i += 1
                self.cols[node] = i # build node:column mapping
                for feature in node_features:
                    shingles = shingle_extraction.extract_shingles(feature)
                    fingerprints = fingerprint.get_fingerprints(shingles)
                    for fp in fingerprints:
                        if not ch_mat.has_key(fp):
                            ch_mat[fp] = []
                        ch_mat[fp].append(i)
            return ch_mat
        
        ch_mat = build_characteristic_matrix(feature_lists)
        for i in ch_mat.keys(): # row i of M
            ch_mat_row_i = ch_mat[i]
            for j in ch_mat_row_i: # column j of M
                # we consider only (i, j) pairs for which M(i, j) = 1
                for l in range(len(self.hash_functions)):
                    h = self.hash_functions[l]
                    h_of_i = h(i)
                    if h_of_i < self.matrix[l, j]:
                        self.matrix[l, j] = h_of_i
    
#     def extend_sketch_matrix(self, feature_lists, new_cols_count, extension_id):
#         new_matrix = np.full((self.h_count, len(self.cols) + new_cols_count), np.iinfo(np.uint64).max, np.uint64)
#         new_matrix[:, :, -new_cols_count] = self.matrix
#         self.matrix = new_matrix
#         
#         j = len(self.cols) - 1
#         for node, feature_list in feature_lists:
#             j += 1
#             self.cols["{0}/{1}".format(extension_id, node)] = j
#             for feature in feature_list:
#                 cached_shingles_dict = {}
#                 for l in range(len(self.hash_functions)):
#                     h = self.hash_functions[l]
#                     i = fingerprint.get_minhash_fingerprint_naive(feature, h, cached_shingles_dict) # row i of matrix M
#                     h_of_i = h(i)
#                     if h_of_i < self.matrix[l, j]:
#                         self.matrix[l, j] = h_of_i
    
    def save_to_file(self, out_file, compress=True):
        if compress:
            with contextlib.closing(gzip.GzipFile(out_file, "wb")) as outfl:
                pickle.dump(self, outfl, pickle.HIGHEST_PROTOCOL)
        else:
            outfl = open(out_file, "wb")
            pickle.dump(self, outfl, pickle.HIGHEST_PROTOCOL)
            outfl.close() 
    
    @staticmethod
    def load_from_file(in_file, compress=True):
        if compress:
            with contextlib.closing(gzip.GzipFile(in_file, "rb")) as infl:
                sketch_matrix = pickle.load(infl)
        else:
            infl = open(in_file, "rb")
            sketch_matrix = pickle.load(infl)
            infl.close()
        assert type(sketch_matrix) is SketchMatrix
        return sketch_matrix
    
    def __repr__(self):
        return str(self.matrix)

    def __init__(self, k, L, hypergraph=None, r_in=0, r_out=0, r_all=0, wl_iterations=0, hash_functions=None, matrix=None, cols=None):
        self.k = k
        self.L = L
        self.h_count = k * L
        
        if hypergraph is not None:
            self.matrix = np.full((self.h_count, hypergraph.number_of_nodes()), np.iinfo(np.uint64).max, np.uint64)
            if type(hash_functions) is list:
                assert len(hash_functions) == k * L
                self.hash_functions = hash_functions
            else:
                self.hash_functions = MinHashFunction.generate_functions(self.h_count)
            self.cols = {}
            
            feature_lists = feature_extraction.get_feature_lists(hypergraph, r_in, r_out, r_all, wl_iterations)
            self.build_sketch_matrix(feature_lists)
        else:
            self.matrix = matrix
            self.cols = cols
