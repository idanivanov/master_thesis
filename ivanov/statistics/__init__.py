'''
Created on Feb 26, 2016

@author: Ivan Ivanov
'''

from sklearn.metrics import roc_curve as sk_roc_curve 
from sklearn.metrics import roc_auc_score, precision_score, recall_score, accuracy_score
from ivanov.graph import dataset_manager
from itertools import imap
import numpy as np
import math

def prepare_target_with_predictions(svm_light_val_file, predictions_file):
    val_data = dataset_manager.read_svm_light_bool_data(svm_light_val_file)
    pred_f = open(predictions_file)
    
    real_targets = imap(lambda x: x[0], val_data)
    pred_targets = imap(float, pred_f.readlines())
    
    return real_targets, pred_targets

def get_probabilities(pred_targets):
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))
    
    targets_prob = imap(sigmoid, pred_targets)
    
    return targets_prob

def prepare_target_with_probabilities(svm_light_val_file, predictions_file):
    real_targets, pred_targets = prepare_target_with_predictions(svm_light_val_file, predictions_file)
    targets_prob = get_probabilities(pred_targets)
    return real_targets, targets_prob

def all_scores(svm_light_val_file, predictions_file, threshold=0.5):
    real_targets, targets_prob = prepare_target_with_probabilities(svm_light_val_file, predictions_file)
    real_targets = list(real_targets)
    targets_prob = list(targets_prob)
    
    pred_targets = map(lambda x: 1 if x >= threshold else -1, targets_prob)
    
    auc = roc_auc_score(real_targets, targets_prob)
    acc = accuracy_score(real_targets, pred_targets)
    prec = precision_score(real_targets, pred_targets)
    rec = recall_score(real_targets, pred_targets)
    
    return auc, acc, prec, rec

def roc_curve(svm_light_val_file, predictions_file):
    real_targets, targets_prob = prepare_target_with_probabilities(svm_light_val_file, predictions_file)
    return sk_roc_curve(real_targets, targets_prob)

def auc(svm_light_val_file, predictions_file):
    real_targets, targets_prob = prepare_target_with_probabilities(svm_light_val_file, predictions_file)
    real_targets = list(real_targets)
    targets_prob = list(targets_prob)
    return roc_auc_score(real_targets, targets_prob)

def accuracy(svm_light_val_file, predictions_file, threshold=0.5):
    real_targets, targets_prob = prepare_target_with_probabilities(svm_light_val_file, predictions_file)
    pred_targets = map(lambda x: 1 if x >= threshold else -1, targets_prob)
    return accuracy_score(real_targets, pred_targets)

def precision(svm_light_val_file, predictions_file, threshold=0.5):
    real_targets, targets_prob = prepare_target_with_probabilities(svm_light_val_file, predictions_file)
    pred_targets = map(lambda x: 1 if x >= threshold else -1, targets_prob)
    return precision_score(real_targets, pred_targets)

def recall(svm_light_val_file, predictions_file, threshold=0.5):
    real_targets, targets_prob = prepare_target_with_probabilities(svm_light_val_file, predictions_file)
    pred_targets = map(lambda x: 1 if x >= threshold else -1, targets_prob)
    return recall_score(real_targets, pred_targets)
