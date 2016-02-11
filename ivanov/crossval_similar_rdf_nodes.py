'''
Created on Feb 9, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_nodes_mining import crossval
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import rdf
from ivanov import helpers

dataset = "famont"
wl_iter_range = range(0, 5)
k_L_range = [
    (25, 14),   # inflation point 0.1
    (25, 58),   # inflation point 0.15
    (25, 265),  # inflation point 0.2
    (15, 211),  # inflation point 0.3
    (10, 165),  # inflation point 0.4
    (5, 32)     # inflation point 0.5
#     (15, 75),   # inflation point 0.25
#     (15, 92),   # inflation point 0.26
#     (15, 112),   # inflation point 0.27
#     (15, 138),   # inflation point 0.28
#     (15, 170),   # inflation point 0.29
#     (15, 261),   # inflation point 0.31
#     (14, 221),   # inflation point 0.32
#     (14, 272),   # inflation point 0.33
#     (13, 222),   # inflation point 0.34
#     (13, 270),   # inflation point 0.35
]
p_range = [4]
r_in_range = range(1, 4)
r_out_range = range(1, 4)
r_all_range = [0]

output_dir = "../output_rdf/crossval_test/"

if __name__ == '__main__':
    in_files = helpers.datasets[dataset]["files"]
    graph, node_id_map = rdf.convert_rdf_to_nx_graph(in_files, discard_classes=False)
    hypergraph = Hypergraph(graph)
    best_model = crossval.loo_crossval(hypergraph, wl_iter_range, r_in_range, r_out_range, r_all_range, output_dir, k_L_range=k_L_range)
    print "Best model:", best_model
