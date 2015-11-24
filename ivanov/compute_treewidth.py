'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from graph.algorithms import arnborg_proskurowski
from ivanov.graph import nxext
from graph import algorithms
from graph import rdf
from ivanov.graph.hypergraph import Hypergraph
import codecs
from ivanov.statistics import treewidth

def compute_rballs_tw(in_file):
    graph = rdf.convert_rdf_to_nx_graph(in_file)
    
    for r in [2, 3, 4, 5]:
        for d in ["in", "out", "all"]:
            if d == "all" and r > 3:
                break
            print r, d
            out_file = codecs.open("../output/tw_r{0}_{1}".format(r, d), "w", "utf8")
             
            i = 0
            for node in graph.nodes_iter():
                rball = algorithms.r_ball(graph, node, r, -1 if d == "in" else 1 if d == "out" else 0)
                ap_result = arnborg_proskurowski.get_canonical_representation(rball, False)
                line = u"{0},{1}\n".format(graph.node[node]["labels"][0].replace(u",", u"[comma]"), ap_result[0])
                out_file.write(line)
#                 print i, line
#                 nxext.visualize_graph(rball, node_labels=True, edge_labels=False)
                i += 1
             
            out_file.close()

if __name__ == '__main__':
#     compute_rballs_tw("../data/family.rdf.owl.rdf")
    
    print treewidth.aggregate("../output/tw_r3_all")
    