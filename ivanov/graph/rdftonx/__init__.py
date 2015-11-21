'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

import networkx as nx
import codecs
import simplejson as sj
from rdflib import Graph as RDFGraph
import rdflib
from ivanov.graph import nxext

def convert_rdf_to_nx_graph(in_file, out_file):
    rdf_graph = RDFGraph()
    rdf_graph.parse(in_file, format=rdflib.util.guess_format(in_file))
    
    nx_graph = nx.MultiDiGraph()
    
    nodes = rdf_graph.all_nodes()
    triples = rdf_graph.triples((None, None, None))
    
    node_id = 0
    node_id_map = {}
    for node in nodes:
        # TODO: how to deal with literals?
        nx_graph.add_node(node_id, labels=[unicode(node)])
        node_id_map[unicode(node)] = node_id
        node_id += 1
    
    for s, p, o in triples:
        s_id = node_id_map[unicode(s)]
        o_id = node_id_map[unicode(o)]
        nx_graph.add_edge(s_id, o_id, label=unicode(p))
    
    nxext.visualize_graph(nx_graph, node_labels=False, edge_labels=False)

in_file = "../../../data/family.rdf.owl.rdf"
convert_rdf_to_nx_graph(in_file, "")
