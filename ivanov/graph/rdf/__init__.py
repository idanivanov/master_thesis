'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from rdflib import Graph as RDFGraph
from rdflib import RDF, RDFS, OWL
import networkx as nx
import rdflib
from owlready import *
from rdflib.term import URIRef

def read_graph(in_files, file_format=None):
    rdf_graph = RDFGraph()
    
    for in_file in in_files:
        rdf_graph.parse(in_file, format=file_format if file_format else rdflib.util.guess_format(in_file))
    
    return rdf_graph

def convert_rdf_to_nx_graph(in_files):
    rdf_graph = read_graph(in_files)
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
    
    return nx_graph

def iri(prefix, suffix):
    return unicode(prefix) + unicode(suffix)

def stats(rdf_graph):
    def get_nodes_of_type(class_type):
        return set(rdf_graph.subjects(RDF.type, URIRef(class_type)))
    
    def get_all_classes():
        nodes_rdf_class = get_nodes_of_type(RDFS.Class)
        nodes_owl_class = get_nodes_of_type(OWL.Class)
        return nodes_rdf_class | nodes_owl_class
    
    classes = get_all_classes()
    nodes_by_class = {cls: get_nodes_of_type(cls) for cls in classes}
    for cls in nodes_by_class:
        print cls, len(nodes_by_class[cls])
    # TODO: get numbers, intersections, blah blah blah...
