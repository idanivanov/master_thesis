'''
Created on Feb 4, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import crossval
from ivanov.graph import dataset_manager
from ivanov import helpers

dataset = "mutagenicity"
wl_iter_range = range(0, 12)
k_L_range = [
    (20, 1),     # inflection point ~0.
    (25, 14),    # inflection point 0.1
    (25, 58),    # inflection point 0.15
    (25, 265),   # inflection point 0.2
    (15, 75),    # inflection point 0.25
    (15, 92),    # inflection point 0.26
    (15, 112),   # inflection point 0.27
    (15, 138),   # inflection point 0.28
    (15, 170),   # inflection point 0.29
    (15, 211),   # inflection point 0.3
    (15, 261),   # inflection point 0.31
    (14, 221),   # inflection point 0.32
    (14, 272),   # inflection point 0.33
    (13, 222),   # inflection point 0.34
    (13, 270),   # inflection point 0.35
    (10, 165),   # inflection point 0.4
    (5, 32),     # inflection point 0.5
    (5, 98),     # inflection point 0.6
    (4, 123),    # inflection point 0.7
    (3, 125),    # inflection point 0.8
    (2, 100),    # inflection point 0.9
    (1, 200)     # inflection point ~1.
]
p_range = range(189)
infl_point_range = [0., 0.0000001, 0.1, 0.15, 0.2, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]
output_dir = "../output_chem/crossval_test/"

if __name__ == '__main__':
    in_file = helpers.datasets[dataset]["files"][0]
    graph_database, chem_props = dataset_manager.read_chemical_compounts(in_file)
    cols_count = len(graph_database)
    target_values = map(lambda x: x[1], chem_props)
    best_model = crossval.loo_crossval_sketch(graph_database, cols_count, target_values, wl_iter_range, k_L_range, output_dir)
#     best_model = crossval.loo_crossval_pnn(graph_database, cols_count, target_values, wl_iter_range, p_range, output_dir)
#     best_model = crossval.loo_crossval_threshold(graph_database, cols_count, target_values, wl_iter_range, infl_point_range, output_dir)
    print "Best model:", best_model
