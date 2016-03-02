'''
Created on Mar 1, 2016

@author: Ivan Ivanov
'''
from sklearn.cross_validation import train_test_split
from ivanov.graph import dataset_manager
from scipy.sparse import csr_matrix
from sklearn import neighbors
import numpy as np
from collections import Counter
import itertools
from ivanov import statistics

class PositiveNeighbors(object):
    # TODO: Find a better name for the module.
    
    def __init__(self, data, records_count, input_dimensions, positive_label=1):
        '''Constructor
        :param data: Input data, where each record is a tuple of the form (target, props), where props is a sparse vector.
        '''
        self.X = csr_matrix((records_count, input_dimensions), dtype=np.int8)
        self.y = np.empty(records_count, dtype=np.int8)
        
        for i, (target, props) in enumerate(data):
            self.y[i] = 1 if target == 2 else target
            for prop in props:
                self.X[i, prop] = 1
        
#         self.appr_nn = neighbors.LSHForest().fit(self.X)
        self.exact_nn = neighbors.NearestNeighbors(algorithm="auto").fit(self.X)
        
        min_k_for_positive = 0
        
        X_to_check = self.X[(self.y == positive_label),:]
        
        for k in range(1, records_count + 1):
            print k, np.shape(X_to_check)
#             neigh = self.appr_nn.kneighbors(X_to_check, n_neighbors=k+1, return_distance=False)
            neigh = self.exact_nn.kneighbors(X_to_check, n_neighbors=k+1, return_distance=False)
            neigh = neigh[:, 1:] # remove self from neighbors
            neigh_targets = np.vectorize(lambda x: self.y[x])(neigh)
            have_no_positive_neighbors = np.apply_along_axis(lambda row: not np.in1d(positive_label, row)[0], 1, neigh_targets)
            X_to_check = X_to_check[have_no_positive_neighbors, :]
            if np.shape(X_to_check)[0] == 0:
                min_k_for_positive = k
                break
        
        print min_k_for_positive
    
    @staticmethod
    def classify_appr_knn():
        X = csr_matrix((records_count, input_dimensions), dtype=np.int8)
        y = np.empty(records_count, dtype=np.int8)
        
        for i, (target, props) in enumerate(data):
            y[i] = target
            for prop in props:
                X[i, prop] = 1
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
        appr_nn = neighbors.LSHForest().fit(X_train)
        similar_records = appr_nn.kneighbors(X_test, n_neighbors=2, return_distance=False)
        similar_targets = np.vectorize(lambda x: y_train[x])(similar_records)
        
        y_test_pred = np.apply_along_axis(statistics.predict_target_majority, 1, similar_targets)
        
        print y_test
        print y_test_pred
        print y_test == y_test_pred
    
print "Start"
# data_file = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/mutagenicity/data/mut_data_wl_3"
data_file = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/nci_hiv/data/AM_vs_I/svm_light_data_wl_8"
data = dataset_manager.read_svm_light_bool_data(data_file)
# records_count = 188
# input_dimensions = 766
records_count = 42687
input_dimensions = 3200132
pn = PositiveNeighbors(data, records_count, input_dimensions)
print "Done"
