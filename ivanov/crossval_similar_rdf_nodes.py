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
    (20, 1),    # inflation point ~0.
    (15, 5),    # inflation point 0.1
    (10, 9),    # inflation point 0.2
    (7, 12),    # inflation point 0.3
    (5, 13),    # inflation point 0.4
    (4, 16),    # inflation point 0.5
    (3, 16),    # inflation point 0.6
    (2, 11),    # inflation point 0.7
    (2, 25),    # inflation point 0.8
    (1, 10),    # inflation point 0.9
    (1, 20),    # inflation point ~1.
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
