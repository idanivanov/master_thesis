'''
Created on Dec 21, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_nodes_mining import feature_extraction
from ivanov.external_lib import sPickle
# from numbapro import vectorize, uint64
from numpy import random
import numpy as np

class SketchMatrix(object):
    @staticmethod
    def generate_hash_functions(h_count):
        def hash_perm(x, a, b, r, prime):
            assert r < prime
            assert 1 <= a <= prime - 1
            assert 0 <= b <= prime - 1
            return ((a * x + b) % prime) % r
        
        def func_generator(_a, _b, _r, _prime):
            f = lambda x: hash_perm(x, _a, _b, _r, _prime)
            return f
        
        # the biggest prime that fits in 64 bits
        prime = 18446744073709551557 # TODO: this prime should be bigger than r!!!
        r = np.iinfo(np.uint64).max
        hash_funcs = []
        
        for _ in range(h_count):
            a = random.randint(1, prime - 1)
            b = random.randint(0, prime - 1)
            
            hash_funcs.append(func_generator(a, b, r, prime))
        
        return hash_funcs
    
    @staticmethod
    def get_minhash_fingerprint_naive(feature, h):
        return 0 # TODO: implement naive version
    
    # TODO: GPU implementation?
#     @vectorize(['uint64[:,:](, )'], target='cpu')
    def build_sketch_matrix(self, feature_lists):
        j = -1
        for node, feature_list in feature_lists:
            j += 1
            self.cols[node] = j
            for feature in feature_list:
                for l in range(len(self.hash_functions)):
                    h = self.hash_functions[l]
                    i = SketchMatrix.get_minhash_fingerprint_naive(feature, h) # row i of M
                    h_of_i = h(i)
                    if h_of_i < self.matrix[l, j]:
                        self.matrix[l, j] = h_of_i
    
    def extend_sketch_matrix(self, feature_lists, new_cols_count, extension_id):
        new_matrix = np.full((self.h_count, len(self.cols) + new_cols_count), np.iinfo(np.uint64).max, np.uint64)
        new_matrix[:, :, -new_cols_count] = self.matrix
        self.matrix = new_matrix
        
        j = len(self.cols) - 1
        for node, feature_list in feature_lists:
            j += 1
            self.cols["{0}/{1}".format(extension_id, node)] = j
            for feature in feature_list:
                for l in range(len(self.hash_functions)):
                    h = self.hash_functions[l]
                    i = SketchMatrix.get_minhash_fingerprint_naive(feature, h) # row i of M
                    h_of_i = h(i)
                    if h_of_i < self.matrix[l, j]:
                        self.matrix[l, j] = h_of_i
    
    def save_to_file(self, out_file):
        outfl = open(out_file, "wb")
        sPickle.s_dump_elt(self, outfl)
        outfl.close() 
    
    def load_from_file(self, in_file):
        infl = open(in_file, "rb")
        sketch_matrix = sPickle.s_load(infl)
        infl.close()
        assert type(sketch_matrix) is SketchMatrix
        return sketch_matrix

    def __init__(self, k, L, hypergraph):
        self.k = k
        self.L = L
        self.h_count = k * L
        self.matrix = np.full((self.h_count, hypergraph.number_of_nodes(), np.iinfo(np.uint64).max, np.uint64))
        self.hash_functions = SketchMatrix.generate_hash_functions(self.h_count)
        self.cols = {}
        
        feature_lists = feature_extraction.get_feature_lists(hypergraph)
        self.build_sketch_matrix(feature_lists)
