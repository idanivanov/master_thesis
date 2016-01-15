'''
Created on Dec 17, 2015

@author: Ivan Ivanov
'''

from unidecode import unidecode
import cPickle as pickle
import contextlib
import codecs
import ntpath
import gzip
import io

def get_file_name(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def file_unicode_to_ascii(in_file, out_file):
    infl = codecs.open(in_file, "r", "utf8")
    outfl = open(out_file, "w")
    
    lines = map(lambda line: unidecode(line), infl.readlines())
    outfl.writelines(lines)
    
    infl.close()
    outfl.close()

def files_unicode_to_ascii(in_files, out_dir):
    for in_file in in_files:
        out_file = out_dir + get_file_name(in_file)
        file_unicode_to_ascii(in_file, out_file)

def save_to_file(obj, out_file, compress=True):
    if compress:
        with contextlib.closing(gzip.GzipFile(out_file, "wb")) as outfl:
            pickle.dump(obj, outfl, pickle.HIGHEST_PROTOCOL)
    else:
        outfl = open(out_file, "wb")
        pickle.dump(obj, outfl, pickle.HIGHEST_PROTOCOL)
        outfl.close()

def load_from_file(in_file, compressed=True):
    if compressed:
        with contextlib.closing(gzip.GzipFile(in_file, "rb")) as infl:
            obj = pickle.load(infl)
    else:
        infl = open(in_file, "rb")
        obj = pickle.load(infl)
        infl.close()
    return obj
