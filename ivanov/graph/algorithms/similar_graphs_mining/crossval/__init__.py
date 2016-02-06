'''
Created on Feb 3, 2016

@author: Ivan Ivanov

Cross-validation for similar graphs mining.
'''
from ivanov.graph.algorithms.similar_graphs_mining.characteristic_matrix import CharacteristicMatrix
from ivanov.graph.algorithms.similar_graphs_mining.sketch_matrix import SketchMatrix
from collections import Counter
import numpy as np

def model(quality, wl_iterations, k, L):
    return {"quality": quality, "wl_iterations": wl_iterations, "k": k, "L": L}

def loo_crossval(graph_database, cols_count, target_values, wl_iter_range, k_L_range, output_dir):
    '''Leave-one-out cross-validation.
    :param graph_database: Defined the same way as for CHaracteristicMatrix constructor.
    :param cols_count: Number of elements in the database.
    :param target_values: A list of the size of the graph_database, where each element
    indicates the real target value of the corresponding (by index) element in the database.
    :param wl_iter_range: Range of Weisfeiler-Lehman iterations to be considered in the cross-validation.
    :param k_L_range: A range okf (k, L) tuples for the sketch matrix to be considered in the cross-validation.
#     :param quality_function: a function with signature (G, sketch_matrix), where G is a list of graphs
#     representing a single entity in the database and sketch_matrix is a sketch matrix. The function
#     should return a real value. The cross-validation will find the model that maximizes this function.
    :param output_dir: A local directory, that will be used to save the sketch matrices of all models.
    :return The best model as a dictionary in the form: {quality, wl_iterations}.
    '''
    def predict_target(similar_targets):
        '''Naive majority election of target.
        '''
        if similar_targets:
            target_counts = Counter(similar_targets)
            majority_label = max(target_counts, key=lambda x: target_counts[x])
            return majority_label
        else:
            return 0
    
    def quality(i, sketch_matrix):
        col_i = sketch_matrix.get_column(i)
        similar_cols = list(sketch_matrix.get_similar_columns(col_i))
        similar_cols.remove(i)
        similar_targets = map(lambda c: target_values[c], similar_cols)
        true_target_i = target_values[i]
        extimated_target_i = predict_target(similar_targets)
        return int(true_target_i == extimated_target_i) # zero-one loss
    
    best_model = model(-1, -1, -1, -1)
    
    for wl_iterations in wl_iter_range:
        ch_matrix = CharacteristicMatrix(graph_database, cols_count, wl_iterations=wl_iterations)
        for k, L in k_L_range:
            sketch_matrix = SketchMatrix(k, L, ch_matrix)
            sketch_matrix.save_to_file(output_dir + "sketch_matrix_wl{0}_k{1}_L{2}".format(wl_iterations, k, L))
            avg_quality = 0.
            for i in range(cols_count):
                avg_quality += float(quality(i, sketch_matrix))
            avg_quality /= cols_count
            print model(avg_quality, wl_iterations, k, L)
            if avg_quality > best_model["quality"]:
                best_model = model(avg_quality, wl_iterations, k, L)
    
    return best_model
                    
