'''
Created on Dec 21, 2015

@author: Ivan Ivanov
'''

import numpy as np

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
    
    # invert dict to map from column index to node id
    cols_nodes_map = {sketch_matrix.cols[node_id] : node_id for node_id in sketch_matrix.cols}
     
    return np.triu(similarity_matrix), cols_nodes_map

# TODO: very naive way of extracting similar nodes
def get_similar_nodes(similarity_matrix, cols_nodes_map):
    similar_nodes = []
    
    for row_index in range(len(similarity_matrix)):
        row = similarity_matrix[row_index]
        col_indices = np.flatnonzero(row)
        if col_indices.size:
            indices = [row_index] + list(col_indices)
            similar = map(lambda index: cols_nodes_map[index], indices)
            similar_nodes.append(similar)
    
    return similar_nodes
