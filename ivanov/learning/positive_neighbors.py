'''
Created on Mar 1, 2016

@author: Ivan Ivanov
'''
from scipy.sparse import vstack
from sklearn import neighbors
import numpy as np

class PositiveNeighbors(object):
    '''This class defines a model for computing the proportion of positive examples, 
    among all positive examples, for which it is true that there is at least one other
    positive example among their neighbors (for the given number of nearest neighbors).
    '''
    
    def __init__(self, n_neighbors, approximate=False, positive_label=1):
        '''Constructor
        :param n_neighbors: Number of nearest neighbors.
        :param approximate: If True will use and approximate nearest neighbor algorithm. Default is False.
        :param positive_label: The positive label in the input data. Default is 1.
        '''
        self.positive_label = positive_label
        
        if approximate:
            self.nn = neighbors.LSHForest(n_neighbors=n_neighbors)
        else:
            self.nn = neighbors.NearestNeighbors(n_neighbors=n_neighbors, algorithm="auto")
    
    def fit(self, X, y):
        '''Fit the model to the input data.
        :param X: Input data.
        :param y: Target labels of the input data.
        :return: Self.
        '''
        self.X = X
        self.y = y
        
        self.nn.fit(self.X)
        
        return self
    
    def predict(self, X_test, y_test):
        '''Compute the proportion of positive test examples which satisfy the
        condition (to have at least one positive neighbor in the training data)
        for the given number of nearest neighbors.
        :param X_test: Input test data.
        :param y_test: Target labels of the input test data.
        :return: The proportion of positive test examples satisfying the condition
        among all positive test examples.
        '''
        positive_X = X_test[(y_test == self.positive_label),:]
        neigh = self.nn.kneighbors(positive_X, return_distance=False)
        neigh_targets = np.vectorize(lambda x: self.y[x])(neigh)
        have_positive_neighbors = np.apply_along_axis(lambda row: np.in1d(self.positive_label, row)[0], 1, neigh_targets)
        prediction = float(np.sum(have_positive_neighbors)) / float(np.shape(positive_X)[0]) 
        return prediction
    
    @staticmethod
    def cross_validate(X, y, n_neighbors, folds_count=10, approximate=False, positive_label=1):
        '''Cross-validate the prediction using the given number of folds.
        :param X: Input data.
        :param y: Target labels of the input data.
        :param n_neighbors: Number of nearest neighbors.
        :param folds_count: Number of cross-validation folds.
        :param approximate: If True will use and approximate nearest neighbor algorithm. Default is False.
        :param positive_label: The positive label in the input data. Default is 1.
        '''
        fold_size = len(y) / folds_count
        fold_offset = 0
        fold_offset_end = 0
        
        avg_prediction = 0.
        
        for _ in range(folds_count):
            fold_offset_end += fold_size
            X_train = vstack([X[:fold_offset], X[fold_offset_end:]])
            y_train = np.hstack((y[:fold_offset], y[fold_offset_end:]))
            X_test = X[fold_offset:fold_offset_end]
            y_test = y[fold_offset:fold_offset_end]
            pn = PositiveNeighbors(n_neighbors=n_neighbors, approximate=approximate, positive_label=positive_label)
            pn.fit(X_train, y_train)
            avg_prediction += pn.predict(X_test, y_test)
            fold_offset = fold_offset_end
        
        avg_prediction /= float(folds_count)
        
        return avg_prediction
