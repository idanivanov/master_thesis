'''
Created on Feb 3, 2016

@author: Ivan Ivanov

Cross-validation for similar graphs mining.
'''
from ivanov.graph.algorithms.similar_graphs_mining.characteristic_matrix import CharacteristicMatrix
from ivanov.graph.algorithms.similar_graphs_mining.sketch_matrix import SketchMatrix
from ivanov.statistics import all_scores_prob
from ivanov import statistics
import numpy as np
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

def model_score(score, wl_iterations, k=-1, L=-1, infl_point=-1, base_model = {}):
    if k != -1 and L != -1:
        infl_point = SketchMatrix.get_inflation_point(k, L)
    m = base_model.copy()
    m.update({
        "auc": score[0],
        "accuracy": score[1],
        "precision": score[2],
        "recall": score[3],
        "wl_iterations": wl_iterations,
        "k": k,
        "L": L,
        "infl_point": infl_point
    })
    return m

def loo_crossval_sketch(graph_database, wl_iter_range, k_L_range, output_dir, base_model={}, cols_count=None):
    '''Leave-one-out cross-validation.
    :param graph_database: Defined the same way as for CharacteristicMatrix constructor (but cannot be a generator).
    :param wl_iter_range: Range of Weisfeiler-Lehman iterations to be considered in the cross-validation.
    :param k_L_range: A range of (k, L) tuples for the sketch matrix to be considered in the cross-validation.
#     :param quality_function: a function with signature (G, sketch_matrix), where G is a list of graphs
#     representing a single entity in the database and sketch_matrix is a sketch matrix. The function
#     should return a real value. The cross-validation will find the model that maximizes this function.
    :param output_dir: A local directory, that will be used to save the sketch matrices of all models.
    :param base_model: A base model that is going to be extended by the new parameters.
    :return The best model as a dictionary.
    '''
    def quality(i, sketch_matrix):
        col_i = sketch_matrix.get_column(i)
        similar_cols = list(sketch_matrix.get_similar_columns(col_i))
        if i in similar_cols:
            similar_cols.remove(i)
        similar_targets = map(lambda c: graph_database[c][2], similar_cols)
        true_target_i = graph_database[i][2]
        estimated_target_i = statistics.predict_target_majority(similar_targets)
#         print "Col:", i, ", Target:", true_target_i, ", Est. target: ", estimated_target_i
#         print "Similar cols:", similar_cols
#         print "Similar targets:", similar_targets
#         print "--------------------------------------"
#         fp = open(output_dir + "classification_sketch", "a")
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
    if not cols_count:
        cols_count = len(graph_database)
    
    models_file = open(output_dir + "models_sketch", "a")
    
    for wl_iterations in wl_iter_range:
#         start = time.time()
        ch_matrix = CharacteristicMatrix(graph_database, cols_count, wl_iterations=wl_iterations, print_progress=True)
#         print "Building characteristic matrix for wl_iter =", wl_iterations, "took:", time.time() - start
        for k, L in k_L_range:
#             start = time.time()
            sketch_matrix = SketchMatrix(k, L, ch_matrix)
#             print "Building sketch matrix for k={0} and L={1} took:".format(k, L), time.time() - start
#             sketch_matrix.save_to_file(output_dir + "sketch_matrix_wl{0}_k{1}_L{2}".format(wl_iterations, k, L))
#             start = time.time()
            avg_quality = 0.
            for i in range(cols_count):
                avg_quality += float(quality(i, sketch_matrix))
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

def loo_crossval_naive(graph_database, wl_iter_range, param_2_range, quality_function, output_dir, base_model={}):
    '''Similar to loo_crossval_sketch but computes directly the Jaccard
    similarities between the columns in the characteristic matrix,
    without using a sketch matrix. Not applicable for big datasets.
    '''
    best_model = model_p(-1, -1, -1, base_model=base_model)
    cols_count = len(graph_database)
    
    models_file = open(output_dir + "models_naive", "a")
    
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

def loo_crossval_threshold(graph_database, wl_iter_range, infl_point_range, output_dir, base_model={}):
    '''Similar to loo_crossval_sketch but computes directly the Jaccard
    similarities between the columns in the characteristic matrix,
    without using a sketch matrix. Not applicable for big datasets.
    :param infl_point_range: A range of inflation point values (infl_point = 1. - threshold).
    '''
    def quality(i, jaccard_similarity_matrix, infl_point):
        threshold = 1. - infl_point
        similar_cols = np.where(jaccard_similarity_matrix[i, :] >= threshold)[0]
        similar_targets = map(lambda c: graph_database[c][2], similar_cols)
        true_target_i = graph_database[i][2]
        estimated_target_i = statistics.predict_target_majority(similar_targets)
#         print "Col:", i, ", Target:", true_target_i, ", Est. target: ", estimated_target_i
#         print "Similar cols:", similar_cols
#         print "Similar targets:", similar_targets
#         print "--------------------------------------"
#         fp = open(output_dir + "classification_threshold", "a")
#         fp.write("Col: {0}, Target: {1}, Est. target: {2}\n".format(i, true_target_i, estimated_target_i))
#         fp.write("Similar cols: {0}\n".format(similar_cols))
#         fp.write("Similar targets: {0}\n".format(similar_targets))
#         fp.write("--------------------------------------\n")
#         fp.close()
        if type(true_target_i) is list:
            return int(estimated_target_i in true_target_i) # zero-one loss
        else:
            return int(true_target_i == estimated_target_i) # zero-one loss
    
    return loo_crossval_naive(graph_database, wl_iter_range, infl_point_range, quality, output_dir, base_model)

def loo_crossval_pnn(graph_database, wl_iter_range, p_range, output_dir, base_model={}):
    '''Similar to loo_crossval_sketch but computes directly the Jaccard
    similarities between the columns in the characteristic matrix,
    without using a sketch matrix. Not applicable for big datasets.
    The classification is done by the p-nearest neighbors method.
    '''    
    def quality_pnn(i, jaccard_similarity_matrix, p):
        '''Quality estimation by p nearest neighbors classification.
        '''
        k_most_similar_cols = jaccard_similarity_matrix[i, :].argsort()[-p:]
        k_most_similar_targets = map(lambda c: graph_database[c][2], k_most_similar_cols)
        true_target_i = graph_database[i][2]
        estimated_target_i = statistics.predict_target_majority(k_most_similar_targets)
        if type(true_target_i) is list:
            return int(estimated_target_i in true_target_i) # zero-one loss
        else:
            return int(true_target_i == estimated_target_i) # zero-one loss
    
    return loo_crossval_naive(graph_database, wl_iter_range, p_range, quality_pnn, output_dir, base_model)

def d_folds(d, sketch_matrix, cols_count, quality_function, targets):
    def aggregate_scores(aggr_score, current_score):
        for i in range(len(aggr_score)):
            aggr_score[i] += current_score[i]
        return aggr_score
    
    def average_score(total_score, folds_count):
        avg_score = []
        for s in total_score:
            avg_score.append(float(s) / float(folds_count))
        return avg_score
    
    fold_size = sketch_matrix.cols_count / d
    raw_matrix = sketch_matrix.matrix
    fold_offset = 0
    fold_offset_end = 0
    # score: AUC, accuracy, precision, recall
    avg_score = [0., 0., 0., 0.]
    
    for _ in range(d):
        fold_offset_end += fold_size
        train_sketch_1 = raw_matrix[:, :fold_offset]
        train_sketch_2 = raw_matrix[:, fold_offset_end:]
        train_sketch = np.concatenate((train_sketch_1, train_sketch_2), axis=1)
        train_targets = targets[:fold_offset] + targets[fold_offset_end:]
        test_targets = targets[fold_offset : fold_offset_end]
        test_sketch = raw_matrix[:, fold_offset : fold_offset_end]
        current_score = quality_function(sketch_matrix, train_sketch, test_sketch, train_targets, test_targets)
        avg_score = aggregate_scores(avg_score, current_score)
        fold_offset = fold_offset_end
    avg_score = average_score(avg_score, d)
    
    return avg_score

def d_fold_crossval(data, cols_count, d, k_L_range, output_dir, base_model={}):
    '''Cross-validation in d-folds.
    :param data: Input data, where each record is a tuple of the form (target, props), where props is a sparse vector.
    :param cols_count: Number of records in data.
    :param d: Number of cross-validation folds.
    :param k_L_range: A range of (k, L) tuples for the sketch matrix to be considered in the cross-validation.
    :param output_dir: A local directory, that will be used to save the sketch matrices of all models.
    :param base_model: A base model that is going to be extended by the new parameters.
    :return: The best model as a dictionary.
    '''
    def quality(sketch_matrix, train_sketch, test_sketch, train_targets, test_targets):
        k = sketch_matrix.k
        L = sketch_matrix.L
        train_cols_count = np.shape(train_sketch)[1]
        test_targets_proba = np.empty(len(test_targets))
        for i in range(np.shape(test_sketch)[1]):
            col_i = test_sketch[:, i : i + 1]
            similar_cols = SketchMatrix._get_similar_columns(col_i, train_sketch, k, L, train_cols_count)
            similar_targets = map(lambda c: train_targets[c], similar_cols)
            estimated_target_proba_i = statistics.predict_binary_target_proba(similar_targets)
            test_targets_proba[i] = estimated_target_proba_i
        
        return all_scores_prob(test_targets, test_targets_proba)
        
    best_model = model_score([-1., -1., -1., -1.], -1, base_model=base_model)
    
    models_file = open(output_dir + "models_sketch", "a")
    
    start = time.time()
    ch_matrix = CharacteristicMatrix(records=data, cols_count=cols_count, print_progress=True)
    targets = ch_matrix.target_values
    print "Building characteristic matrix took:", time.time() - start
    for k, L in k_L_range:
        start = time.time()
        sketch_matrix = SketchMatrix(k, L, ch_matrix)
        print "Building sketch matrix for k={0} and L={1} took:".format(k, L), time.time() - start
#         sketch_matrix.save_to_file(output_dir + "sketch_matrix_wl{0}_k{1}_L{2}".format(wl_iterations, k, L))
        start = time.time()
        avg_score = d_folds(d, sketch_matrix, cols_count, quality, targets)
        print "Classification took:", time.time() - start
        current_model = model_score(avg_score, "outer", k, L, base_model=base_model)
        print current_model
        models_file.write(str(current_model) + ",\n")
        models_file.flush()
        if avg_score[0] > best_model["auc"]:
            best_model = current_model
    
    if not base_model:
        # print best model when there are no outer parameters
        models_file.write("Best model: " + str(best_model) + "\n")
    
    models_file.close()
    
    return best_model
