'''
Created on Feb 4, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import crossval
from ivanov.graph import dataset_manager
from ivanov import helpers
from itertools import imap

dataset = "mutagenicity"
wl_iter_range = range(0, 12)
k_L_range = [
    (20, 1),    # inflection point ~0.
    (15, 5),    # inflection point 0.1
    (10, 9),    # inflection point 0.2
    (7, 12),    # inflection point 0.3
    (7, 16),    # inflection point 0.33
    (5, 13),    # inflection point 0.4
    (4, 16),    # inflection point 0.5
    (3, 16),    # inflection point 0.6
    (2, 11),    # inflection point 0.7
    (2, 25),    # inflection point 0.8
    (1, 10),    # inflection point 0.9
    (1, 20),    # inflection point ~1.
]
p_range = range(30)
infl_point_range = [0., 0.0000001, 0.1, 0.15, 0.2, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]
output_dir = "../output_chem/"

def crossval_small_dataset(w_shingles):
    in_file = helpers.datasets[dataset]["files"][0]
    graph_database = list(dataset_manager.read_chemical_compounts(in_file))
#     best_model = crossval.loo_crossval_sketch(graph_database, wl_iter_range, k_L_range, output_dir, cols_count=188, w_shingles=w_shingles)
    best_model = crossval.loo_crossval_pnn(graph_database, wl_iter_range, p_range, output_dir, w_shingles=w_shingles)
#     best_model = crossval.loo_crossval_threshold(graph_database, wl_iter_range, infl_point_range, output_dir, w_shingles=w_shingles)
    print "Best model:", best_model

def crossval_big_dataset():
    path_to_data = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/nci_hiv/data/A_vs_M/"
    examples_count = 1503
    folds_count = 10
    data_file = path_to_data + "svm_light_data_wl_{0}"
    for wl_iterations in wl_iter_range:
        data = dataset_manager.read_svm_light_bool_data(data_file.format(wl_iterations))
        data = imap(lambda tup: (1 if tup[0] == 2 else -1, tup[1]), data) # TODO: only for A_vs_M
        base_model = {"wl_iterations": wl_iterations}
        best_model = crossval.d_fold_crossval(data, examples_count, folds_count, k_L_range, output_dir, base_model=base_model)
        print "Best model:", best_model

def crossval_small_rdf_dataset(w_shingles):
    in_files = helpers.datasets[dataset]["files"]
    compounds_targets_file = helpers.datasets[dataset]["compounds_targets"]["sample-1"]
    uri_prefix = "http://dl-learner.org/mutagenesis#"
    graph_database = list(dataset_manager.prepare_rdf_chemical_data(in_files, compounds_targets_file, uri_prefix))
#     best_model = crossval.loo_crossval_sketch(graph_database, wl_iter_range, k_L_range, output_dir, cols_count=188, w_shingles=w_shingles)
#     best_model = crossval.loo_crossval_pnn(graph_database, wl_iter_range, p_range, output_dir, w_shingles=w_shingles)
    best_model = crossval.loo_crossval_threshold(graph_database, wl_iter_range, infl_point_range, output_dir, w_shingles=w_shingles)
    print "Best model:", best_model

if __name__ == '__main__':
    crossval_small_dataset(True)
#     crossval_big_dataset()
#     crossval_small_rdf_dataset(True)
