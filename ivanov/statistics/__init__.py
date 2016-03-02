'''
Created on Feb 26, 2016

@author: Ivan Ivanov
'''

from sklearn.metrics import roc_auc_score, precision_score, recall_score, accuracy_score
from sklearn.metrics import roc_curve as sk_roc_curve 
from ivanov.graph import dataset_manager
from collections import Counter
from itertools import imap
import numpy as np
import math
import itertools

def predict_target_majority(targets, default_negative_target=0):
    '''Majority election of target.
    :param similar_targets: A list of either integers or lists. Each element may have multiple target values.
    The target label that appears most frequently is the chosen one.
    '''
    if len(targets):
        if type(targets[0]) is list:
            target_counts = Counter(itertools.chain(*targets))
        else:
            target_counts = Counter(targets)
        majority_label = max(target_counts, key=lambda x: target_counts[x])
        return majority_label
    else:
        return default_negative_target

def predict_binary_target_proba(targets, positive_target=1):
    '''Get the probability that the chosen target will be positive given the input targets.
    '''
    if targets:
        if type(targets[0]) is list:
            targets = itertools.chain(*targets)
        target_counts = Counter(targets)
        assert len(target_counts) <= 2
        predict_proba = float(target_counts[positive_target]) / float(len(targets))
        return predict_proba
    else:
        return 0.

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

def all_scores(real_targets, pred_targets, threshold=0.5):
    targets_prob = list(get_probabilities(pred_targets))
    return all_scores_prob(real_targets, targets_prob, threshold)

def all_scores_prob(real_targets, targets_prob, threshold=0.5):
    pred_targets_thr = map(lambda x: 1 if x >= threshold else -1, targets_prob)
    
    auc = roc_auc_score(real_targets, targets_prob)
    acc = accuracy_score(real_targets, pred_targets_thr)
    prec = precision_score(real_targets, pred_targets_thr)
    rec = recall_score(real_targets, pred_targets_thr)
    
    return auc, acc, prec, rec

def all_scores_from_files(svm_light_val_file, predictions_file, threshold=0.5):
    real_targets, pred_targets = prepare_target_with_predictions(svm_light_val_file, predictions_file)
    real_targets = list(real_targets)
    pred_targets = pred_targets
    
    return all_scores(real_targets, pred_targets, threshold)

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
