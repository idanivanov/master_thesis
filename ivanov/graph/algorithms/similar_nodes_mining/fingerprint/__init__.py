'''
Created on Dec 30, 2015

@author: Ivan Ivanov
'''

import numpy as np

irred_poly_64_list = [64, 60, 59, 57, 56, 55, 54, 53, 52, 51, 50, 48, 45, 44, 41, 37, 36, 34, 33, 31, 29, 27, 26, 23, 20, 19, 18, 11, 8, 5, 3, 1, 0]
irred_poly_64_bin = [1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1]

def rabin_fingerprint(binary_shingle):
    '''Calculates Rabin's fingerprint of a shingle
    given by its binary representation.
    :param binary_shingle: A binary representation of a shingle.
    :return Rabin's fingerprint of the shingle as integer.
    '''
    pass # TODO: implement Rabin's fingerprint.

def get_minhash_fingerprint_naive(feature, h):
    '''Get naively the fingerprint of the shingle which has minimal
    index (wrt the permutation defined by h) among all shingles
    contained in the feature.
    :param feature: a Networkx graph.
    :param h: a hash function defining a permutation of fingerprints.
    :return An integer fingerprint of a shingle.
    '''
    return 0 # TODO: implement naive version

def irreducible_poly_list_to_bin_array(irred_poly_list):
    degree = max(irred_poly_list)
    poly_bin = np.zeros(degree + 1, dtype=np.int)
    for i in irred_poly_list:
        poly_bin[i] = 1
    return poly_bin
