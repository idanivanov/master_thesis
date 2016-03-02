'''
Created on Jan 13, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import feature_extraction,\
    shingle_extraction, fingerprint
from ivanov.inout.serializable import Serializable
import numpy as np
import itertools

class CharacteristicMatrix(Serializable):
    
#     @staticmethod
#     def estimate_time_to_build(nodes_count, features_per_node = 100):
#         '''Get the estimated time to build the characteristic matrix in seconds.
#         '''
#         time_per_feature = 0.001
#         return nodes_count * features_per_node * time_per_feature
    
    def build(self, feature_lists):
        self.sparse_matrix = {}
        i = -1
        for _, record_features, _ in feature_lists:
            i += 1
            if self.print_progress:
                print "Ch.Mat.: Processing column", i, "of", self.cols_count
            for feature in record_features:
                shingles = shingle_extraction.extract_shingles(feature)
                fingerprints = fingerprint.get_fingerprints(shingles)
                for fp in fingerprints:
                    if not self.sparse_matrix.has_key(fp):
                        self.sparse_matrix[fp] = set()
                    self.sparse_matrix[fp].add(i)
    
    def build_from_records(self, records):
        self.target_values = []
        self.sparse_matrix = {}
        i = -1
        for target, record_props in records:
            i += 1
            self.target_values.append(target)
            if self.print_progress:
                print "Ch.Mat.: Processing column", i, "of", self.cols_count
            for property in record_props:
#                 fingerprints = fingerprint.get_fingerprints(shingles)
#                 for fp in fingerprints:
                # TODO: potential problem for the SketchMatrix because the properties are not fingerprints
                if not self.sparse_matrix.has_key(property):
                    self.sparse_matrix[property] = set()
                self.sparse_matrix[property].add(i)
    
    def compute_column_fingerprints(self, record_graphs):
        assert self.wl_state
        features = []
        for hypergraph in record_graphs:
            new_features, self.wl_state = feature_extraction.extract_features(hypergraph, self.wl_iterations, self.wl_state)
            features += new_features
        
        column = set()
        
        for feature in features:
            shingles = shingle_extraction.extract_shingles(feature)
            fingerprints = fingerprint.get_fingerprints(shingles)
            column |= set(fingerprints)
        
        return sorted(column)
    
    def compute_jaccard_similarity_matrix(self):
        cols_cache = {}
        def get_shingles_fp_set(col):
            if col in cols_cache:
                return cols_cache[col]
            else:
                shingles_fp = set()
                for row in self.sparse_matrix:
                    if col in self.sparse_matrix[row]:
                        shingles_fp.add(row)
                cols_cache[col] = shingles_fp
                return shingles_fp
        
        def jaccard_sim(u, v):
            len_union = len(u.union(v))
            if len_union > 0:
                return float(len(u.intersection(v))) / float(len_union)
            else:
                return 0.
        
        jaccard_sim_mat = np.zeros((self.cols_count, self.cols_count), dtype=np.float32)
        
        for col_1, col_2 in itertools.combinations(range(self.cols_count), 2):
            shingles_col_1 = get_shingles_fp_set(col_1)
            shingles_col_2 = get_shingles_fp_set(col_2)
            similarity = jaccard_sim(shingles_col_1, shingles_col_2)
            jaccard_sim_mat[col_1, col_2] = similarity
            jaccard_sim_mat[col_2, col_1] = similarity
        
        return jaccard_sim_mat
    
    def non_empty_rows(self):
        return self.sparse_matrix.keys()
    
    def non_empty_rows_count(self):
        return len(self.sparse_matrix.keys())
    
    def __getitem__(self, key):
        return self.sparse_matrix[key]
    
    def __eq__(self, other):
        if isinstance(other, CharacteristicMatrix):
            return self.sparse_matrix == other.sparse_matrix
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __init__(self, graph_database=None, cols_count=None, wl_iterations=0, print_progress=False, records=None):
        '''A sparse binary matrix M having records as columns and fingerprints as rows.
        M(i, j)=1 iff record j has a shingle with fingerprint i.
        :param graph_database: A list of tuples where each tuple has the form
        (record_id, graphs, target_values) and represents an element of the database (will be
        represented by a column in the characteristic matrix). The field graphs is
        a list of Hypergraphs (One element can be represented by multiple graphs) and
        the field target_values is a list of target labels for the record.
        :param wl_iterations: Number of Weisfeiler-Lahman iterations to be
        performed (before a graph becomes 'stable').
        '''
        self.cols_count = cols_count
        self.print_progress = print_progress
        self.wl_iterations = wl_iterations
        
        if graph_database:
            if isinstance(graph_database, list):
                feature_lists, self.wl_state = feature_extraction.get_feature_lists(graph_database, wl_iterations, iterator=False)
            else:
                self.wl_state = None
                feature_lists = feature_extraction.get_feature_lists(graph_database, wl_iterations)
            
            self.build(feature_lists)
        else:
            assert records
            self.build_from_records(records)
