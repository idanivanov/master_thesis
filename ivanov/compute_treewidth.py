'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from graph.algorithms import arnborg_proskurowski
from ivanov.graph import nxext
from graph import algorithms
from graph import rdf
from ivanov.graph.hypergraph import Hypergraph

if __name__ == '__main__':
    
    in_file = "../data/family.rdf.owl.rdf"
    graph = rdf.convert_rdf_to_nx_graph(in_file)
    
    out_file = open("../output/tw_r2_in", "w")
    
    i = 0
    for node in graph.nodes_iter():
        rball = algorithms.r_ball(graph, node, 2, -1)
#         nxext.visualize_graph(rball, node_labels=False, edge_labels=False)
        # TODO: strange behavior, the labels from AP are assigned to the original graph. Why?
        ap_result = arnborg_proskurowski.get_canonical_representation(rball, False)
        line = "{0},{1}\n".format(graph.node[node]["labels"][0], ap_result[0])
        out_file.write(line)
        print i, line
        i += 1
    
    out_file.close()
    