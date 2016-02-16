'''
Created on Feb 3, 2016

@author: Ivan Ivanov

Cross-validation for similar graphs mining.
'''
from ivanov.graph.algorithms.similar_graphs_mining.characteristic_matrix import CharacteristicMatrix
from ivanov.graph.algorithms.similar_graphs_mining.sketch_matrix import SketchMatrix
from collections import Counter
import numpy as np
import itertools
import time

def model(quality, wl_iterations, base_model = {}):
    m = base_model.copy()
    m.update({"quality": quality, "wl_iterations": wl_iterations})
    return m

def model_infl_point(quality, wl_iterations, k=-1, L=-1, infl_point=-1, base_model = {}):
    if k != -1 and L != -1:
        infl_point = SketchMatrix.get_inflation_point(k, L)
    m = model(quality, wl_iterations, base_model)
    m.update({"k": k, "L": L, "infl_point": infl_point})
    return m

def model_p(quality, wl_iterations, p, base_model = {}):
    m = model(quality, wl_iterations, base_model)
    m.update({"p": p})
    return m

def predict_target_majority(similar_targets):
        '''Majority election of target.
        :param similar_targets: A list of either integers or lists. Each element may have multiple target values.
        The target label that appears most frequently is the chosen one.
        '''
        if similar_targets:
            if type(similar_targets[0]) is list:
                target_counts = Counter(itertools.chain(*similar_targets))
            else:
                target_counts = Counter(similar_targets)
            majority_label = max(target_counts, key=lambda x: target_counts[x])
            return majority_label
        else:
            return 0

def loo_crossval_sketch(graph_database, cols_count, target_values, wl_iter_range, k_L_range, output_dir, base_model={}, prepare_query_function=None):
    '''Leave-one-out cross-validation.
    :param graph_database: Defined the same way as for CharacteristicMatrix constructor.
    :param cols_count: Number of elements in the database.
    :param target_values: A list of the size of the graph_database, where each element
    indicates the real target value of the corresponding (by index) element in the database.
    :param wl_iter_range: Range of Weisfeiler-Lehman iterations to be considered in the cross-validation.
    :param k_L_range: A range okf (k, L) tuples for the sketch matrix to be considered in the cross-validation.
#     :param quality_function: a function with signature (G, sketch_matrix), where G is a list of graphs
#     representing a single entity in the database and sketch_matrix is a sketch matrix. The function
#     should return a real value. The cross-validation will find the model that maximizes this function.
    :param output_dir: A local directory, that will be used to save the sketch matrices of all models.
    :param base_model: A base model that is going to be extended by the new parameters.
    :param prepare_query_function: A function to prepare the query record that is left out by the cross-validation.
    :return The best model as a dictionary in the form: {quality, wl_iterations}.
    '''
    def quality(i, ch_matrix, sketch_matrix):
        if prepare_query_function:
            col_i = prepare_query_function(i, graph_database, ch_matrix, sketch_matrix)
        else:
            col_i = sketch_matrix.get_column(i)
        similar_cols = list(sketch_matrix.get_similar_columns(col_i))
        if i in similar_cols:
            similar_cols.remove(i)
        similar_targets = map(lambda c: target_values[c], similar_cols)
        true_target_i = target_values[i]
        estimated_target_i = predict_target_majority(similar_targets)
#         print "Col:", i, ", Target:", true_target_i, ", Est. target: ", estimated_target_i
#         print "Similar cols:", similar_cols
#         print "Similar targets:", similar_targets
#         print "--------------------------------------"
#         fp = open(output_dir + "classification", "a")
#         fp.write("Col: {0}, Target: {1}, Est. target: {2}\n".format(i, true_target_i, estimated_target_i))
#         fp.write("Similar cols: {0}\n".format(similar_cols))
#         fp.write("Similar targets: {0}\n".format(similar_targets))
#         fp.write("--------------------------------------\n")
#         fp.close()
        if type(true_target_i) is list:
            return int(estimated_target_i in true_target_i) # zero-one loss
        else:
            return int(true_target_i == estimated_target_i) # zero-one loss
    
    best_model = model_infl_point(-1, -1, base_model=base_model)
    
    models_file = open(output_dir + "models", "a")
    
    for wl_iterations in wl_iter_range:
#         start = time.time()
        ch_matrix = CharacteristicMatrix(graph_database, cols_count, wl_iterations=wl_iterations, print_progress=False)
#         print "Building characteristic matrix for wl_iter =", wl_iterations, "took:", time.time() - start
        for k, L in k_L_range:
#             start = time.time()
            sketch_matrix = SketchMatrix(k, L, ch_matrix)
#             print "Building sketch matrix for k={0} and L={1} took:".format(k, L), time.time() - start
#             sketch_matrix.save_to_file(output_dir + "sketch_matrix_wl{0}_k{1}_L{2}".format(wl_iterations, k, L))
#             start = time.time()
            avg_quality = 0.
            for i in range(cols_count):
                avg_quality += float(quality(i, ch_matrix, sketch_matrix))
            avg_quality /= cols_count
#             print "Classification took:", time.time() - start
            current_model = model_infl_point(avg_quality, wl_iterations, k, L, base_model=base_model)
            print current_model
            models_file.write(str(current_model) + ",\n")
            models_file.flush()
            if avg_quality > best_model["quality"]:
                best_model = current_model
    
    if not base_model:
        # print best model when there are no outer parameters
        models_file.write("Best model: " + str(best_model) + "\n")
    
    models_file.close()
    
    return best_model

def loo_crossval_naive(graph_database, cols_count, target_values, wl_iter_range, param_2_range, quality_function, output_dir, base_model={}):
    '''Similar to loo_crossval_sketch but computes directly the Jaccard
    similarities between the columns in the characteristic matrix,
    without using a sketch matrix. Not applicable for big datasets.
    '''
    best_model = model_p(-1, -1, -1, base_model=base_model)
    
    models_file = open(output_dir + "models", "a")
    
    for wl_iterations in wl_iter_range:
        ch_matrix = CharacteristicMatrix(graph_database, cols_count, wl_iterations=wl_iterations)
        jaccard_similarity_matrix = ch_matrix.compute_jaccard_similarity_matrix()
        for p in param_2_range:
            avg_quality = 0.
            for i in range(cols_count):
                avg_quality += float(quality_function(i, jaccard_similarity_matrix, p))
            avg_quality /= cols_count
            current_model = model_p(avg_quality, wl_iterations, p, base_model=base_model)
            print current_model
            models_file.write(str(current_model) + ",\n")
            models_file.flush()
            if avg_quality > best_model["quality"]:
                best_model = current_model
    
    if not base_model:
        # print best model when there are no outer parameters
        models_file.write("Best model: " + str(best_model) + "\n")
    
    models_file.close()
    
    return best_model

def loo_crossval_threshold(graph_database, cols_count, target_values, wl_iter_range, infl_point_range, output_dir, base_model={}):
    '''Similar to loo_crossval_sketch but computes directly the Jaccard
    similarities between the columns in the characteristic matrix,
    without using a sketch matrix. Not applicable for big datasets.
    :param infl_point_range: A range of inflation point values (infl_point = 1. - threshold).
    '''
    def quality(i, jaccard_similarity_matrix, infl_point):
        threshold = 1. - infl_point
        similar_cols = np.where(jaccard_similarity_matrix[i, :] >= threshold)[0]
        similar_targets = map(lambda c: target_values[c], similar_cols)
        true_target_i = target_values[i]
        estimated_target_i = predict_target_majority(similar_targets)
#         print "Col:", i, ", Target:", true_target_i, ", Est. target: ", estimated_target_i
#         print "Similar cols:", similar_cols
#         print "Similar targets:", similar_targets
#         print "--------------------------------------"
#         fp = open(output_dir + "classification", "a")
#         fp.write("Col: {0}, Target: {1}, Est. target: {2}\n".format(i, true_target_i, estimated_target_i))
#         fp.write("Similar cols: {0}\n".format(similar_cols))
#         fp.write("Similar targets: {0}\n".format(similar_targets))
#         fp.write("--------------------------------------\n")
#         fp.close()
        if type(true_target_i) is list:
            return int(estimated_target_i in true_target_i) # zero-one loss
        else:
            return int(true_target_i == estimated_target_i) # zero-one loss
    
    return loo_crossval_naive(graph_database, cols_count, target_values, wl_iter_range, infl_point_range, quality, output_dir, base_model)

def loo_crossval_pnn(graph_database, cols_count, target_values, wl_iter_range, p_range, output_dir, base_model={}):
    '''Similar to loo_crossval_sketch but computes directly the Jaccard
    similarities between the columns in the characteristic matrix,
    without using a sketch matrix. Not applicable for big datasets.
    The classification is done by the p-nearest neighbors method.
    '''    
    def quality_pnn(i, jaccard_similarity_matrix, p):
        '''Quality estimation by p nearest neighbors classification.
        '''
        k_most_similar_cols = jaccard_similarity_matrix[i, :].argsort()[-p:]
        k_most_similar_targets = map(lambda c: target_values[c], k_most_similar_cols)
        true_target_i = target_values[i]
        estimated_target_i = predict_target_majority(k_most_similar_targets)
        if type(true_target_i) is list:
            return int(estimated_target_i in true_target_i) # zero-one loss
        else:
            return int(true_target_i == estimated_target_i) # zero-one loss
    
    return loo_crossval_naive(graph_database, cols_count, target_values, wl_iter_range, p_range, quality_pnn, output_dir, base_model)
