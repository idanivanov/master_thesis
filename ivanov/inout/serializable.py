'''
Created on Jan 13, 2016

@author: Ivan Ivanov
'''

import cPickle as pickle
import contextlib
import gzip

class Serializable(object):
    '''A class whose instances can be saved to and loaded from a file.
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def save_to_file(self, out_file, compress=True):
        if compress:
            with contextlib.closing(gzip.GzipFile(out_file, "wb")) as outfl:
                pickle.dump(self, outfl, pickle.HIGHEST_PROTOCOL)
        else:
            outfl = open(out_file, "wb")
            pickle.dump(self, outfl, pickle.HIGHEST_PROTOCOL)
            outfl.close() 
    
    @staticmethod
    def load_from_file(in_file, compressed=True):
        if compressed:
            with contextlib.closing(gzip.GzipFile(in_file, "rb")) as infl:
                obj = pickle.load(infl)
        else:
            infl = open(in_file, "rb")
            obj = pickle.load(infl)
            infl.close()
        return obj
