'''
Created on Dec 18, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_nodes_mining.sketch_matrix import SketchMatrix
from ivanov.graph.algorithms import similar_nodes_mining
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import rdf
import helpers
import time

# print "Converting graph..."
# graph, node_id_map = rdf.convert_rdf_to_nx_graph(["../output_2/famont/famont_ext.rdf"], discard_classes=False)
# print "Creating hypergraph..."
# hypergraph = Hypergraph(graph)
# print "Saving hypergraph..."
# hypergraph.save_to_file("../output_2/famont/famont_ext_hgraph")
# print "Done."

# rdf.extend_inferred_knowledge(helpers.datasets["famont"]["files"], "../output_2/famont/famont_ext.rdf")

start = time.time()
hypergraph = Hypergraph.load_from_file("../output_2/famont/famont_ext_hgraph")
print "Reading hypergraph took", time.time() - start, "s"

start = time.time()
sketch_matrix = SketchMatrix(5, 20, hypergraph, r_in=2, r_out=2, r_all=0, wl_iterations=4)
print "Building sketch matrix took", time.time() - start, "s"

start = time.time()
sketch_matrix.save_to_file("../output_2/famont/famont_ext_sketch")
print "Saving sketch matrix took", time.time() - start, "s"

start = time.time()
sim_mat, cols_nodes_map = similar_nodes_mining.get_node_similarity_matrix(sketch_matrix)
print "Building simiarity matrix took", time.time() - start, "s"

start = time.time()
similar_nodes = similar_nodes_mining.get_similar_nodes(sim_mat, cols_nodes_map)
print "Extracting similar nodes took", time.time() - start, "s"

print similar_nodes
