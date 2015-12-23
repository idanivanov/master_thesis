'''
Created on Dec 18, 2015

@author: Ivan Ivanov
'''

from graph.hypergraph import Hypergraph
from graph import rdf
import helpers

graph, node_id_map = rdf.convert_rdf_to_nx_graph(["../output/temp_famont.rdf"], discard_classes=False)
hypergraph = Hypergraph(graph)
hypergraph.save_to_file("../output_2/famont_ext_hgraph")

# hypergraph = Hypergraph.load_from_file("../output_2/famont_ext_hgraph")
# print hypergraph.number_of_nodes(), hypergraph.number_of_edges()

# rdf.extend_infered_knowledge(helpers.datasets["famont"]["files"], "../output/temp_tele.rdf")