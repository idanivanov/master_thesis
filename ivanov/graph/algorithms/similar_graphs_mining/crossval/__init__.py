'''
Created on Feb 3, 2016

@author: Ivan Ivanov

Cross-validation for similar graphs mining.
'''
from ivanov.graph.algorithms.similar_graphs_mining.characteristic_matrix import CharacteristicMatrix
from ivanov.graph.algorithms.similar_graphs_mining.sketch_matrix import SketchMatrix
import numpy as np

def model(quality, wl_iterations, k, L):
    return {"quality": -1, "wl_iterations": -1, "k": -1, "L": -1}

def loo_crossval(graph_database, cols_count, wl_iter_range, k_range, L_range, quality_function, output_dir):
    '''Leave-one-out cross-validation.
    :param graph_database: Defined the same way as for CHaracteristicMatrix constructor.
    :param cols_count: Number of elements in the database.
    :param wl_iter_range: Range of Weisfeiler-Lehman iterations to be considered in the cross-validation.
    :param k_range: Range of k values for the sketch matrix to be considered by the cross-validation.
    :param L_range: Range of L values for the sketch matrix to be considered by the cross-validation.
    :param quality_function: a function with signature (G, sketch_matrix), where G is a list of graphs
    representing a single entity in the database and sketch_matrix is a sketch matrix. The function
    should return a real value. The cross-validation will find the model that maximizes this function.
    :param output_dir: A local directory, that will be used to save the sketch matrices of all models.
    :return The best model as a dictionary in the form: {quality, wl_iterations, k, L}.
    '''
    cols_part_count = cols_count - 1
    best_model = model(-1, -1, -1, -1)
    
    for wl_iterations in wl_iter_range:
        for k in k_range:
            for L in L_range:
                avg_quality = 0.
                for i, G in enumerate(graph_database):
                    graph_database_part = graph_database
                    graph_database_part.remove(i)
                    ch_matrix = CharacteristicMatrix(graph_database_part, cols_part_count, wl_iterations=wl_iterations)
                    sketch_matrix = SketchMatrix(k, L, ch_matrix)
                    sketch_matrix.save_to_file(output_dir + "sketch_matrix_wl{0}_k{1}_L{2}".format(wl_iterations, k, L))
                    avg_quality += quality_function(G, sketch_matrix)
                avg_quality /= cols_count
                print model(avg_quality, wl_iterations, k, L)
                if avg_quality > best_model["quality"]:
                    best_model = model(avg_quality, wl_iterations, k, L)
    
    return best_model
                    
