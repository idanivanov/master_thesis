'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from rdflib.term import URIRef, BNode, Literal
from rdflib import Graph as RDFGraph
from RDFClosure import convert_graph
from rdflib import RDF, RDFS, OWL
import networkx as nx
import rdflib
import codecs
from ivanov import helpers

def read_graph(in_files, file_format=None):
    rdf_graph = RDFGraph()
    
    for in_file in in_files:
        rdf_graph.parse(in_file, format=file_format if file_format else rdflib.util.guess_format(in_file))
    
    return rdf_graph

def convert_rdf_to_nx_graph(in_files, labels = "colors", discard_classes = True):
    '''
    Converts an RDFLib graph to a Networkx graph.
    :param in_files - Files containing the RDF data
    :param labels - Set labels of the Networkx graph to be: (by default) "colors" - nodes have the 
    same color if they are of the same type, edges have the same color if they are of the same
    predicate; "uris" - each node/edge has as label the URI that identifies it in the RDF graph.
    :param discard_classes - If true, will not include any RDF class as a node in the Networkx graph.
    '''
    rdf_graph = read_graph(in_files)
    nx_graph = nx.MultiDiGraph()
    
    nodes = rdf_graph.all_nodes()
    triples = rdf_graph.triples((None, None, None))
    
    node_id = 0
    node_id_map = {}
    if labels == "uris":
        for node in nodes:
            # TODO: how to deal with literals?
            nx_graph.add_node(node_id, labels=[unicode(node)])
            node_id_map[unicode(node)] = node_id
            node_id += 1
        
        for s, p, o in triples:
            s_id = node_id_map[unicode(s)]
            o_id = node_id_map[unicode(o)]
            nx_graph.add_edge(s_id, o_id, label=unicode(p))
    else:
        colors = {
            u"undefined": "0",
            u"bnode": "1", # TODO: is the bnode color needed?
            u"literal": "2", # TODO: is the literal color needed?
            u"http://www.w3.org/2001/XMLSchema#string": "3" # default literal type
        }
        color_id = 4
        
        if discard_classes:
            all_classes = get_all_classes(rdf_graph)
        
        for node in nodes:
            if discard_classes:
                if node in all_classes:
                    # we ignore classes
                    # TODO: what about predicates and other ontology definitions?
                    continue
            node_kind = type(node)
            node_colors = set()
            if node_kind is BNode:
                # add the bnode color
                node_colors.add(colors[u"bnode"])
            if node_kind in [BNode, URIRef]:
                # add a color for each type of the node
                types = list(get_node_types(rdf_graph, node))
                if not types:
                    # if there are not types add unknown color
                    node_colors.add(colors[u"undefined"])
                for node_type in types:
                    node_type_raw = unicode(node_type)
                    if node_type_raw not in colors:
                        colors[node_type_raw] = str(color_id)
                        color_id += 1
                    node_colors.add(colors[node_type_raw])
            elif node_kind is Literal:
                # ad the literal color and the color for the datatype of the literal
                node_colors.add(colors[u"literal"])
                if node._datatype:
                    datatype = unicode(node._datatype)
                    if datatype not in colors:
                        colors[datatype] = str(color_id)
                        color_id += 1
                else:
                    datatype = u"http://www.w3.org/2001/XMLSchema#string"
                node_colors.add(colors[datatype])
            else:
                # for cases like QuotedGraph and others.
                # TODO: not properly handled
                print "Unknown term type."
                node_colors.add(colors[u"undefined"])
            nx_graph.add_node(node_id, labels=node_colors)
            node_id_map[unicode(node)] = node_id
            node_id += 1
        
        for s, p, o in triples:
            if p == RDF.type:
                # skip RDF.type edges
                continue
            if discard_classes:
                if s in all_classes or o in all_classes:
                    # skip edges from/to classes
                    continue
            s_id = node_id_map[unicode(s)]
            o_id = node_id_map[unicode(o)]
            p_raw = unicode(p)
            if p_raw not in colors:
                    colors[p_raw] = str(color_id)
                    color_id += 1
            nx_graph.add_edge(s_id, o_id, label=colors[p_raw])
    
    return nx_graph, node_id_map

def get_node_types(rdf_graph, node):
    return rdf_graph.objects(node, RDF.type)

def get_nodes_of_type(rdf_graph, class_type):
    return rdf_graph.subjects(RDF.type, class_type)

def get_blank_nodes(rdf_graph):
    subjects = rdf_graph.subjects(None, None)
    return filter(lambda node: type(node) is BNode, subjects)

def get_all_classes(rdf_graph):
    from_type = set(rdf_graph.objects(None, RDF.type))
    from_owl = set(rdf_graph.subjects(RDF.type, OWL.Class))
    from_rdfs = set(rdf_graph.subjects(RDF.type, RDFS.Class))
    return from_type | from_owl | from_rdfs

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

def extend_infered_knowledge(in_files, out_file):
    '''
    Uses the RDFClosure reasoner to create
    explicit triples from the inferred knowledge 
    n in_files and saves the complete extensional
    dataset in out_file.
    Note: RDFClosure - http://www.ivan-herman.net/Misc/2008/owlrl/
    '''
    assert type(in_files) in [list, set]
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
    
    options = Options()
    options.sources = in_files
    
    outfl = codecs.open(out_file, "w", "utf8")
    outfl.write(convert_graph(options))
    outfl.close()
