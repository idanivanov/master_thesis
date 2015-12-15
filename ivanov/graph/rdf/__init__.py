'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from rdflib import Graph as RDFGraph
from rdflib import RDF, RDFS, OWL
from rdflib.term import URIRef, BNode
import networkx as nx
import rdflib
import codecs

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

def get_nodes_of_type(rdf_graph, class_type):
    return rdf_graph.subjects(RDF.type, class_type)

def get_blank_nodes(rdf_graph):
    subjects = rdf_graph.subjects(None, None)
    return filter(lambda node: type(node) is BNode, subjects)

def get_all_classes(rdf_graph):
    return set(rdf_graph.objects(None, RDF.type))

def extract_subjects_by_types(rdf_graph, output_dir):
    all_classes = get_all_classes(rdf_graph)
    i = 0
    
    for cls in all_classes:
        fp = codecs.open(output_dir + str(i), "w", "utf-8")
        fp.write(unicode(cls) + u"\n")
        nodes = get_nodes_of_type(rdf_graph, cls)
        nodes_str = map(lambda node: unicode(node) + u"\n", nodes)
        fp.writelines(nodes_str)
        fp.close()
        print "done for", i, cls
        i += 1
