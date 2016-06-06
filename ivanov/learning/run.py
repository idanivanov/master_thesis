'''
Created on Jun 2, 2016

@author: Ivan Ivanov
'''
from ivanov.learning.min_hash_nearest_neighbor import MinHashNearestNeighbor
from sklearn.preprocessing import MultiLabelBinarizer
from ivanov.graph import dataset_manager
from sklearn import cross_validation
from sklearn import grid_search
import numpy as np

def read_data(in_file):
    canon_repr_data = dataset_manager.read_canonical_representations_data(in_file)
    X = []
    y = []
    
    for record in canon_repr_data:
        targets, canon_strings = record
        X.append(canon_strings)
        y.append(targets)
    
    y = MultiLabelBinarizer().fit_transform(y)
    
    return X, y

def score():
    in_file = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/3.8/data_1_in_balls_1000/canon_repr/multilabel_svm_light_data_wl_{0}"
    num_perm = 2048
    w = 10
    threshold = 0.4
    wl_iterations = 1
    label_majority_threshold = 0.5
    scoring = "f1_micro"
    
    print "Reading data..."
    X, y = read_data(in_file.format(wl_iterations))
    
    mhnn = MinHashNearestNeighbor(num_perm=num_perm, w=w, threshold=threshold, label_majority_threshold=label_majority_threshold)
    accuracy = cross_validation.cross_val_score(mhnn, X, y, cv=10, verbose=10, n_jobs=-1, scoring=scoring)
    
    print scoring + ": {0}, (+,-) {1}".format(accuracy.mean(), accuracy.std())

def do_grid_search():
    in_file = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/3.8/data_1_in_balls_1000/canon_repr/multilabel_svm_light_data_wl_{0}"
    out_file = "result_wl_{0}"
    
    wl_iter_range = [0, 1, 2, 3, 4]
    scoring = "f1_micro"
    
    w_range = [5, 10]
    threshold_range = np.arange(0.1, 1.0, 0.1)
#     label_majority_threshold_range = np.arange(0., 1.1, 0.1)
    parameters = {'w': w_range,
                  'threshold': threshold_range,
#                   'label_majority_threshold': label_majority_threshold_range
                 }
    
    all_scores = []
    
    with open(out_file.format('_'.join(map(lambda x: str(x), wl_iter_range))), "w") as out_file:
        for wl_iterations in wl_iter_range:
            print "Computing for wl_iterations", wl_iterations
            X, y = read_data(in_file.format(wl_iterations))
            mhnn = MinHashNearestNeighbor()
            grid_est = grid_search.GridSearchCV(mhnn, parameters, verbose=10, cv=10, n_jobs=-1, scoring=scoring)
            grid_est.fit(X, y)
            best_result = grid_est.best_score_
            best_params = grid_est.best_params_
            line = "{{'wl_it': {0}, 'minhash_params': {1}, '{3}': {2}}},\n".format(wl_iterations, best_params, best_result, scoring)
            out_file.write(line)
            out_file.flush()
            all_scores += grid_est.grid_scores_
        out_file.write("all: " + str(all_scores))

if __name__ == '__main__':
    do_grid_search()
#     score()
    print "Done."