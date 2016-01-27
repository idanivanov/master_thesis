'''
Created on Dec 21, 2015

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import feature_extraction,\
    shingle_extraction, fingerprint
from ivanov.graph.algorithms.similar_graphs_mining.sketch_matrix import SketchMatrix
from ivanov.graph.hypergraph import Hypergraph

def get_similar_graphs(query_graph_list, sketch_matrix, wl_iterations, wl_labels_list):
    '''Get all similar graphs to the query graph list.
    :param query_graph_list: List of graphs representing one query element.
    :param sketch_matrix: A SketchMatrix.
    :param: wl_iterations: Number of Weisfeiler & Lehman iterations to be performed.
    :param: wl_labels_list: List of labels used when building the sketch matrix.
    '''
    def get_shingle_fingerprints():
        def inner():
            for query_graph in query_graph_list:
                if type(query_graph) is Hypergraph:
                    query_hypergraph = query_graph
                else:
                    query_hypergraph = Hypergraph(query_graph)
                
                query_hypergraph_features = feature_extraction.extract_features(query_hypergraph, wl_iterations, wl_labels_list)
                for feature in query_hypergraph_features:
                    shingles = shingle_extraction.extract_shingles(feature)
                    fingerprints = fingerprint.get_fingerprints(shingles)
                    for fingerprint in fingerprints:
                        yield fingerprint
        return set(inner())
    
    shingle_fingerprints = get_shingle_fingerprints()
    
    sketch_column = SketchMatrix.compute_column(shingle_fingerprints)
    
    return sketch_matrix.get_similar_columns(sketch_column)
