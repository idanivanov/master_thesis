'''
Created on Dec 17, 2015

@author: Ivan Ivanov
'''

import codecs
import io
from unidecode import unidecode
import ntpath

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
