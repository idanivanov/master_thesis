'''
Created on Jan 9, 2016

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_nodes_mining import fingerprint
import numpy as np
import random

class MinHashFunction(object):
    
    big_prime = int(18446744073709551629) # the first prime after 2^64
    
    def __init__(self, a, b):
        assert 1 <= a < MinHashFunction.big_prime
        assert 0 <= b < MinHashFunction.big_prime
        self.a = a
        self.b = b
    
    def __call__(self, x):
        p = MinHashFunction.big_prime
        r = fingerprint.max_fingerprint
        return np.uint64(int((int(self.a * int(x)) + self.b) % p) % r)
    
    @staticmethod
    def generate_functions(h_count):
        def randombigint(min_val, max_val, bits=65):
            rand = int(random.getrandbits(65))
            return int((rand % (max_val - min_val + 1)) + min_val)
        
        hash_funcs = []
        
        for _ in range(h_count):
            a = randombigint(1, MinHashFunction.big_prime - 1)
            b = randombigint(0, MinHashFunction.big_prime - 1)
            
            hash_funcs.append(MinHashFunction(a, b))
        
        return hash_funcs
