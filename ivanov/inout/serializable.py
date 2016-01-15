'''
Created on Jan 13, 2016

@author: Ivan Ivanov
'''
from ivanov import inout

class Serializable(object):
    '''A class whose instances can be saved to and loaded from a file.
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def save_to_file(self, out_file, compress=True):
        inout.save_to_file(self, out_file, compress)
    
    @staticmethod
    def load_from_file(in_file, compressed=True):
        return inout.load_from_file(in_file, compressed)
