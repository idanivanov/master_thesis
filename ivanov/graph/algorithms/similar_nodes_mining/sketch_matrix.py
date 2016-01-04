'''
Created on Dec 21, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_nodes_mining import feature_extraction,\
    fingerprint
# from numbapro import vectorize, uint64
import cPickle as pickle
import numpy as np
import contextlib
import random
import gzip

class SketchMatrix(object):
    @staticmethod
    def hash_func_generator(_a, _b, _r, _prime):
        def hash_perm(x, a, b, r, prime):
            assert r < prime
            assert 1 <= a <= prime - 1
            assert 0 <= b <= prime - 1
            return np.uint64(int((int(a * int(x)) + b) % prime) % r)
        f = lambda x: hash_perm(x, _a, _b, _r, _prime)
        return f
    
    @staticmethod
    def generate_hash_functions(h_count):
        def randombigint(min_val, max_val, bits=65):
            rand = int(random.getrandbits(65))
            return (rand % (max_val - min_val + 1)) + min_val
        
        # the first prime after 2^64
        prime = 18446744073709551629
        r = 18446744073709551616 # 2^64
        hash_funcs = []
        
        for _ in range(h_count):
            a = randombigint(1, prime - 1)
            b = randombigint(0, prime - 1)
            
            hash_funcs.append(SketchMatrix.hash_func_generator(a, b, r, prime))
        
        return hash_funcs
    
    # TODO: GPU implementation?
#     @vectorize(['uint64[:,:](, )'], target='cpu')
    def build_sketch_matrix(self, feature_lists):
        j = -1
        for node, feature_list in feature_lists:
            j += 1
            self.cols[node] = j
            for feature in feature_list:
                cached_shingles_dict = {}
                for l in range(len(self.hash_functions)):
                    h = self.hash_functions[l]
                    i = fingerprint.get_minhash_fingerprint_naive(feature, h, cached_shingles_dict) # row i of matrix M
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
                    i = fingerprint.get_minhash_fingerprint_naive(feature, h) # row i of matrix M
                    h_of_i = h(i)
                    if h_of_i < self.matrix[l, j]:
                        self.matrix[l, j] = h_of_i
    
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

    def __init__(self, k, L, hypergraph, r_in=0, r_out=0, r_all=0, wl_iterations=0, hash_functions=None):
        self.k = k
        self.L = L
        self.h_count = k * L
        self.matrix = np.full((self.h_count, hypergraph.number_of_nodes()), np.iinfo(np.uint64).max, np.uint64)
        if type(hash_functions) is list:
            assert len(hash_functions) == k * L
            self.hash_functions = hash_functions
        else:
            self.hash_functions = SketchMatrix.generate_hash_functions(self.h_count)
        self.cols = {}
        
        feature_lists = feature_extraction.get_feature_lists(hypergraph, r_in, r_out, r_all, wl_iterations)
        self.build_sketch_matrix(feature_lists)
