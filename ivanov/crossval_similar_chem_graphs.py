'''
Created on Feb 4, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import crossval
from ivanov.graph import dataset_manager
from ivanov import helpers

dataset = "mutagenicity"
wl_iter_range = range(5)
k_L_range = [
    (25, 14),   # inflation point 0.1
    (25, 58),   # inflation point 0.15
    (25, 265),  # inflation point 0.2
    (15, 211),  # inflation point 0.3
    (10, 165),  # inflation point 0.4
    (5, 32)     # inflation point 0.5
]
output_dir = "../output_chem/crossval_test/"

if __name__ == '__main__':
    in_file = helpers.datasets[dataset]["files"][0]
    graph_database, chem_props = dataset_manager.read_chemical_compounts(in_file)
    cols_count = len(graph_database)
    target_values = map(lambda x: x[1], chem_props)
    best_model = crossval.loo_crossval(graph_database, cols_count, target_values, wl_iter_range, k_L_range, output_dir)
    print "Best model:", best_model
