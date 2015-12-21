'''
Created on Dec 18, 2015

@author: Ivan Ivanov
'''

from graph.hypergraph import Hypergraph
from graph import rdf
import helpers

graph, node_id_map = rdf.convert_rdf_to_nx_graph(helpers.datasets["lexvo"]["files"], discard_classes=True)
hypergraph = Hypergraph(graph)
hypergraph.save_to_file("../output/lexvo_hgraph")