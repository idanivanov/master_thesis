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
    
    def predict(self, X_test):
        '''Compute the proportion of test examples which satisfy the condition
        (to have at least one positive neighbor in the training data) for the
        given number of nearest neighbors.
        :param X_test: Input test data.
        :return: The proportion of test examples satisfying the condition
        among all positive test examples.
        '''
        neigh = self.nn.kneighbors(X_test, return_distance=False)
        neigh_targets = np.vectorize(lambda x: self.y[x])(neigh)
        have_positive_neighbors = np.apply_along_axis(lambda row: np.in1d(self.positive_label, row)[0], 1, neigh_targets)
        prediction = float(np.sum(have_positive_neighbors)) / float(np.shape(X_test)[0]) 
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
        positive_X = X[(y == positive_label)]
        negative_X = X[(y != positive_label)]
        
        fold_size = np.shape(positive_X)[0] / folds_count
        fold_offset = 0
        fold_offset_end = 0
        
        positive_y_train = np.full((np.shape(positive_X)[0] - fold_size,), positive_label)
        negative_y = np.full((np.shape(negative_X)[0],), -1, dtype=np.int16)
        y_train = np.hstack((negative_y, positive_y_train))
        
        avg_prediction = 0.
        
        for _ in range(folds_count):
            fold_offset_end += fold_size
            X_train = vstack([negative_X, positive_X[:fold_offset], positive_X[fold_offset_end:]])
            X_test = positive_X[fold_offset:fold_offset_end]
            pn = PositiveNeighbors(n_neighbors=n_neighbors, approximate=approximate, positive_label=positive_label)
            pn.fit(X_train, y_train)
            avg_prediction += pn.predict(X_test)
            fold_offset = fold_offset_end
        
        avg_prediction /= float(folds_count)
        
        return avg_prediction
