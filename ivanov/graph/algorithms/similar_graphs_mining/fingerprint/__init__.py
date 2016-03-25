'''
Created on Dec 30, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_graphs_mining import shingle_extraction
from ivanov.graph.algorithms import arnborg_proskurowski
from external.ffield import FField
import numpy as np
import time

# irred_poly_64_list = [64, 60, 59, 57, 56, 55, 54, 53, 52, 51, 50, 48, 45, 44, 41, 37, 36, 34, 33, 31, 29, 27, 26, 23, 20, 19, 18, 11, 8, 5, 3, 1, 0]
# irred_poly_64_bin = [1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1]
# irred_poly_64_int = int(30633610468600151985)

# irred_poly_32_list = [32, 31, 30, 26, 24, 23, 21, 19, 15, 14, 13, 11, 10, 6, 3, 2, 0]
# irred_poly_32_bin = [1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1]
# irred_poly_32_int = int(5979908935)

# irred_poly_24_list = [24, 23, 18, 15, 14, 12, 11, 10, 8, 7, 5, 4, 3, 1, 0]
# irred_poly_24_bin = [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1]
# irred_poly_24_int = int(29062723)

# irred_poly_16_list = [16, 13, 12, 11, 9, 7, 5, 4, 3, 2, 0]
# irred_poly_16_bin = [1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1]
# irred_poly_16_int = int(96953)

irred_polys = {
    64: int(30633610468600151985),
    32: int(5979908935),
    24: int(29062723),
    16: int(96953)
}

max_fingerprint = int(18446744073709551616) # 2^64

def rabin_fingerprint(shingle_binary, size=64):
    '''Calculates Rabin's fingerprint of a binary array.
    :param binary_array: A list of binary values.
    :param size: Size of the fingerprint in bits. Possible
    sizes are 64 (default), 32, 24 and 16.
    :return Rabin's fingerprint of the shingle as integer.
    '''
    galois_field = FField(size)
    divident_degree = galois_field.FindDegree(shingle_binary)
    _, fingerprint = galois_field.FullDivision(shingle_binary, irred_polys[size], divident_degree, size)
    return np.uint64(fingerprint)

# TODO: is little- or big-endian better?
def string_bytes_to_int(string_value, big_endian=True):
    '''Converts a string to an integer using each symbol as its byte value.
    :param string_value: String to be converted.
    :param big_endian: (default True) Interpret the bytes in big-endian or little-endian order.
    '''
    enc = "utf8" if type(string_value) is unicode else None
    byte_arr = bytearray(string_value, enc)
    int_value = 0
    
    if big_endian:
        for b in byte_arr:
            int_value = int_value << 8
            int_value += b
    else:
        for i, b in enumerate(byte_arr):
            int_value += (b << (i * 8))
    
    return int_value

def get_fingerprints(shingles, size=64):
    for shingle in shingles:
        shingle_binary = string_bytes_to_int(shingle)
        yield rabin_fingerprint(shingle_binary, size)

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
