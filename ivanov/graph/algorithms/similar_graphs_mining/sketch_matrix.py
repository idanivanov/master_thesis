'''
Created on Dec 21, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_graphs_mining.characteristic_matrix import CharacteristicMatrix
from ivanov.graph.algorithms.similar_graphs_mining.min_hash_function import MinHashFunction
from ivanov.inout.serializable import Serializable
import numpy as np

class SketchMatrix(Serializable):
    @staticmethod
    def get_L(k, inflection_point):
        '''Calculate which value of L leads to inflection_point given k.
        '''
        return int(round(pow((1. / (1. - inflection_point)), k)))
    
    @staticmethod
    def get_inflation_point(k, L):
        '''Calculate inflation point given k and L of the sketch matrix.
        '''
        return 1. - pow(1. / float(L), 1. / float(k))
    
#     @staticmethod
#     def estimate_time_to_build(nodes_count, ch_mat_non_empty_rows, k, L):
#         '''Get the estimated time to build the sketch matrix in seconds.
#         '''
#         time_per_shetch_cell_iteration = 0.00001
#         return nodes_count * ch_mat_non_empty_rows * k * L * time_per_shetch_cell_iteration
    
    @staticmethod
    def _get_similar_columns(sketch_column, raw_sketch_matrix, k, L, cols_count):
        '''Returns the indices of all columns, which evaluate to true
        after being compared to the query sketch column using the AND-
        and OR-amplification rules (see Big Data lectures).
        '''
        equality_sketch = raw_sketch_matrix == sketch_column
        # has a raw for each band
        and_amplifications = np.empty((L, cols_count), np.bool_)
        offset = 0
        for l in range(L):
            offset_new = offset + k
            and_amplifications[l] = equality_sketch[offset : offset_new].all(0)
            offset = offset_new
        or_amplification = and_amplifications.any(0)
        return np.nonzero(or_amplification)[0]
    
    def build(self, ch_matrix):
        for i in ch_matrix.non_empty_rows(): # row i of M
            ch_mat_row_i = ch_matrix[i]
            for j in ch_mat_row_i: # column j of M
                # we consider only (i, j) pairs for which M(i, j) = 1
                for l in range(len(self.hash_functions)):
                    h = self.hash_functions[l]
                    h_of_i = h(i)
                    if h_of_i < self.matrix[l, j]:
                        self.matrix[l, j] = h_of_i
    
    def compute_column(self, shingle_fingerprints):
        '''Computes a sketch column for the list of shingle,
        fingerprints using the same min-hash functions as for
        the rest of the sketch.
        :param shingles: A list of shingles.
        :returns A numpy array representing a sketch column.
        '''
        column = np.full((self.h_count, 1), np.iinfo(np.uint64).max, np.uint64)
        for i in shingle_fingerprints:
            for l in range(len(self.hash_functions)):
                h = self.hash_functions[l]
                h_of_i = h(i)
                if h_of_i < column[l, 0]:
                    column[l, 0] = h_of_i
        return column
    
    def get_column(self, i):
        return self.matrix[:, i : i + 1]
    
    def get_similar_columns(self, sketch_column):
        return SketchMatrix._get_similar_columns(sketch_column, self.matrix, self.k, self.L, self.cols_count)
    
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
        
    def __repr__(self):
        return str(self.matrix)

    def __init__(self, k, L, ch_matrix=None, hash_functions=None, raw_sketch_matrix=None):
        self.k = k
        self.L = L
        self.h_count = k * L
        self.cols_count = ch_matrix.cols_count
        
        if ch_matrix is not None:
            assert isinstance(ch_matrix, CharacteristicMatrix)
            self.matrix = np.full((self.h_count, ch_matrix.cols_count), np.iinfo(np.uint64).max, np.uint64)
            if type(hash_functions) is list:
                assert len(hash_functions) == k * L
                self.hash_functions = hash_functions
            else:
                self.hash_functions = MinHashFunction.generate_functions(self.h_count)
            
            self.build(ch_matrix)
        else:
            self.matrix = raw_sketch_matrix
