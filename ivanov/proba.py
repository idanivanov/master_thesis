'''
Created on Dec 16, 2015

@author: Ivan Ivanov
'''

# http://www.ivan-herman.net/Misc/2008/owlrl/

from RDFClosure import convert_graph
from ivanov import helpers
from ivanov.graph import inout

class Options:
    sources = None
    text = None
    owlClosure = "yes"
    rdfsClosure = "yes"
    owlExtras = "no"
    axioms = False
    daxioms = False
    format = "rdfxml"
    iformat = "auto"
    trimming = False

if __name__ == '__main__':
    options = Options()
    options.sources = helpers.datasets["peel-ascii"]["files"]
      
    print convert_graph(options)
#     out_dir = "../data/ascii/peel/"
#     inout.files_unicode_to_ascii(helpers.datasets["peel"]["files"], out_dir)
