'''
Created on Apr 2, 2016

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_graphs_mining import crossval
from ivanov.graph import dataset_manager

def crossval_multilabel_dataset(path_to_data, examples_count, folds_count, wl_iter_range, k_L_range, prediction_threshold_range, output_dir):
    data_file = path_to_data + "multilabel_svm_light_data_wl_{0}"
    for prediction_threshold in prediction_threshold_range:
        for wl_iterations in wl_iter_range:
            data = dataset_manager.read_svm_light_bool_data(data_file.format(wl_iterations))
            base_model = {"wl_iterations": wl_iterations, "pred_threshold": prediction_threshold}
            best_model = crossval.d_fold_crossval(data, examples_count, folds_count, k_L_range, output_dir, base_model=base_model, multilabel=True, multilabel_prediction_threshold=prediction_threshold)
            print "Best model:", best_model

if __name__ == '__main__':
    
    path_to_data = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/data_1_all_balls/data_w_{0}/"
    output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/"
    examples_count = 10000
    folds_count = 10
    
    window_size_range = [5, 10]
    wl_iter_range = range(5)
    prediction_threshold = [0.4, 0.6]
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
    
    for w in window_size_range:
        crossval_multilabel_dataset(path_to_data.format(w), examples_count, folds_count, wl_iter_range, k_L_range, prediction_threshold, output_dir)
