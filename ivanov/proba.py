'''
Created on Dec 18, 2015

@author: Ivan Ivanov
'''

from graph.hypergraph import Hypergraph
from graph import rdf
import helpers

print "Converting graph..."
graph, node_id_map = rdf.convert_rdf_to_nx_graph(helpers.datasets["geospecies"]["files"], discard_classes=True)
print "Creating hypergraph..."
hypergraph = Hypergraph(graph)
print "Saving hypergraph..."
hypergraph.save_to_file("../output_2/geo_hgraph")
print "Done."

# hypergraph = Hypergraph.load_from_file("../output_2/famont_ext_hgraph")
# print hypergraph.number_of_nodes(), hypergraph.number_of_edges()

# rdf.extend_inferred_knowledge(helpers.datasets["famont"]["files"], "../output/temp_tele.rdf")