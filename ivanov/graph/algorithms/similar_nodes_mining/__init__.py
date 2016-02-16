'''
Created on Jan 26, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms import r_ball_hyper, similar_graphs_mining
import numpy as np

def extract_rballs_of_node(node, hypergraph, r_in=0, r_out=0, r_all=0):
    rballs = [r_ball_hyper(hypergraph, node, r_in, edge_dir=-1) if r_in > 0 else None,
              r_ball_hyper(hypergraph, node, r_out, edge_dir=1) if r_out > 0 else None,
              r_ball_hyper(hypergraph, node, r_all, edge_dir=0) if r_all > 0 else None]
    
    return filter(lambda x: x is not None, rballs)

def extract_rballs_database(hypergraph, r_in=0, r_out=0, r_all=0):
    '''Extract the r-ball(s) around each node in the hypergraph.
    :return (graph_database, index_node_map) - graph_database to
    be used for characteristic matrix; index_node_map mapping
    indices in the graph_database to node ids in the hypergraph
    '''
    def rballs_database_generator():
        for node in hypergraph.nodes_iter():
            yield node, extract_rballs_of_node(node, hypergraph, r_in, r_out, r_all)
    
    index_node_map = {}
    i = 0
    for node in hypergraph.nodes_iter():
        index_node_map[i] = node
        i += 1
    
    return rballs_database_generator(), index_node_map

# TODO: can be optimized, since now we compute all symmetries
def get_node_similarity_matrix(sketch_matrix):
    sketch = sketch_matrix.matrix
    nodes_count = np.shape(sketch)[1]
    k = sketch_matrix.k
    L = sketch_matrix.L
    
    similarity_matrix = np.zeros((nodes_count, nodes_count))
    
    for n1 in range(nodes_count):
        n1_sketch_col = sketch[:, n1 : n1 + 1]
        equality_sketch_for_n1 = sketch == n1_sketch_col
        bands_amplification = np.empty((L, nodes_count))
        offset = 0
        for l in range(L):
            offset_new = offset + k
            bands_amplification[l] = equality_sketch_for_n1[offset : offset_new].all(0)
            offset = offset_new
        similarity_matrix[n1] = bands_amplification.any(0)
    
    np.fill_diagonal(similarity_matrix, 0.)
    
    return np.triu(similarity_matrix)

def get_similar_nodes(node, hypergraph, sketch_matrix, wl_iterations, wl_labels_list, r_in=0, r_out=0, r_all=0):
    rballs = extract_rballs_of_node(node, hypergraph, r_in, r_out, r_all)
    return similar_graphs_mining.get_similar_graphs(rballs, sketch_matrix, wl_iterations, wl_labels_list)

# TODO: very naive way of extracting all similar nodes
def get_all_similar_nodes(similarity_matrix, cols_nodes_map):
    similar_nodes = []
    
    for row_index in range(len(similarity_matrix)):
        row = similarity_matrix[row_index]
        col_indices = np.flatnonzero(row)
        if col_indices.size:
            indices = [row_index] + list(col_indices)
            similar = map(lambda index: cols_nodes_map[index], indices)
            similar_nodes.append(similar)
    
    return similar_nodes
