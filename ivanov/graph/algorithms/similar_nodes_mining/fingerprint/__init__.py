'''
Created on Dec 30, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_nodes_mining import shingle_extraction
from ivanov.graph.algorithms import arnborg_proskurowski
import numpy as np

# irred_poly_64_list = [64, 60, 59, 57, 56, 55, 54, 53, 52, 51, 50, 48, 45, 44, 41, 37, 36, 34, 33, 31, 29, 27, 26, 23, 20, 19, 18, 11, 8, 5, 3, 1, 0]
irred_poly_64_bin = [1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1]
powers_of_2 = np.power(np.uint64(2), np.arange(np.uint64(64))[::-1])

max_fingerprint = int(18446744073709551616) # 2^64

def rabin_fingerprint(binary_array):
    '''Calculates Rabin's fingerprint of a binary array.
    :param binary_array: A list of binary values.
    :return Rabin's fingerprint of the shingle as integer.
    '''
    def remove_zeroes_left(_binary_array):
        '''Removes zeroes from the left part of a binary representation.
        :param _binary_shingle: A binary matrix.
        '''
        if np.sum(_binary_array) > 0:
            start = np.argwhere(_binary_array)[0]
            return _binary_array[start:]
        return _binary_array[-1:]
    
    def mod(a, b):
        '''Modulo division of two binary arrays (polynomials).
        :param a: poly dividend
        :param b: poly divisor
        '''
        b = np.pad(b, (0, len(a) - len(b)), 'constant', constant_values=(0, 0))
        return a ^ b
    
    remainder = remove_zeroes_left(binary_array)
    
    while len(remainder) >= len(irred_poly_64_bin):
        remainder = mod(remainder, irred_poly_64_bin)
        remainder = remove_zeroes_left(remainder)

    fingerprint = np.uint64(np.sum(np.multiply(remainder, powers_of_2[64 - len(remainder):])))

    return fingerprint

def string_to_binary_array(string_value):
    '''Converts a string to a binary array.
    :param string_value: String to be converted.
    '''
    byte_string = np.fromstring(string_value, np.ubyte)
    return np.unpackbits(byte_string)

def get_fingerprints(shingles):
    for shingle in shingles:
        yield rabin_fingerprint(string_to_binary_array(shingle))

def get_minhash_fingerprint_naive(feature, h, cached_shingles_dict=None):
    '''Get naively the fingerprint of the shingle which has minimal
    index (wrt the permutation defined by h) among all shingles
    contained in the feature.
    :param feature: a Networkx graph.
    :param h: a hash function defining a permutation of fingerprints.
    :param cached_shingles_dict (optional): A dictionary of the form {feature_id : set_of_fingerprints_of_shingles}
    :return An integer fingerprint of a shingle.
    '''
    if type(cached_shingles_dict) is dict:
        _, feature_id = arnborg_proskurowski.get_canonical_representation(feature)
        if feature_id in cached_shingles_dict:
            fingerprints = cached_shingles_dict[feature_id]
        else:
            shingles = shingle_extraction.extract_shingles(feature)
            fingerprints = set(get_fingerprints(shingles))
            cached_shingles_dict[feature_id] = fingerprints
    else:
        shingles = shingle_extraction.extract_shingles(feature)
        fingerprints = get_fingerprints(shingles)
    return min(fingerprints, key=h)

def irreducible_poly_list_to_bin_array(irred_poly_list):
    degree = max(irred_poly_list)
    poly_bin = np.zeros(degree + 1, dtype=np.int)
    for i in irred_poly_list:
        poly_bin[i] = 1
    return poly_bin
