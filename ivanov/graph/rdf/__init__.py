'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from rdflib.term import URIRef, BNode, Literal
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph as RDFGraph
from RDFClosure import convert_graph
from rdflib import RDF, RDFS, OWL
from ivanov import helpers
import networkx as nx
import rdflib
import codecs

def read_graph(in_files, file_format=None):
    rdf_graph = RDFGraph()
    
    for in_file in in_files:
        rdf_graph.parse(in_file, format=file_format if file_format else rdflib.util.guess_format(in_file))
    
    return rdf_graph

def convert_rdf_to_nx_graph(in_files, labels="colors", discard_classes=True, test_mode=False, return_colors=False, base_colors=None, next_color_id=None):
    '''Converts an RDFLib graph to a Networkx graph.
    :param in_files: Files containing the RDF data.
    :param labels (optional): Set labels of the Networkx graph to be: (by default) "colors" - nodes have the 
    same color if they are of the same type, edges have the same color if they are of the same
    predicate (all rdf:type edges will be removed); "uris" - each node/edge has as label the URI that identifies it in the RDF graph.
    :param discard_classes (optional): If true, will not include any RDF class as a node in the Networkx graph.
    :param test_mode: Used for unit testing. If True sorts the nodes in the graph by URIs.
    :param return_colors: (default False) If True, includes the colors mapping as part of the result.
    :param base_colors: A pre-difined mapping of RDF types to color id's to be used and extended.
    :param next_color_id: An integer with which the new color id's will start.
    :return: (nx_graph, uri_node_map[, colors, next_color_id])
    '''
    assert type(in_files) in [list, set]
    
    rdf_graph = read_graph(in_files)
    return convert_rdf_graph_to_nx_graph(rdf_graph, labels=labels, discard_classes=discard_classes, test_mode=test_mode, return_colors=return_colors, base_colors=base_colors, next_color_id=next_color_id)

def convert_rdf_graph_to_nx_graph(rdf_graph, labels="colors", discard_classes=True, test_mode=False, return_colors=False, base_colors=None, next_color_id=None):
    nx_graph = nx.MultiDiGraph()
    
    if test_mode:
        # sort all RDF elements so the color ID's are consistent in multiple passes
        nodes = sorted(list(rdf_graph.all_nodes()))
        triples = sorted(list(rdf_graph.triples((None, None, None))))
    else:
        nodes = rdf_graph.all_nodes()
        triples = rdf_graph.triples((None, None, None))
    
    node_id = 0
    uri_node_map = {}
    if labels == "uris":
        for node in nodes:
            u_node = unicode(node)
            if u_node not in uri_node_map:
                # Note: one node for all literals with the same value
                nx_graph.add_node(node_id, labels=[u_node])
                uri_node_map[u_node] = node_id
                node_id += 1
        
        for s, p, o in triples:
            s_id = uri_node_map[unicode(s)]
            o_id = uri_node_map[unicode(o)]
            nx_graph.add_edge(s_id, o_id, label=unicode(p))
    else:
        thing_uri = u"http://www.w3.org/2002/07/owl#Thing"
        if base_colors:
            colors = base_colors
            color_id = next_color_id
        else:
            colors = {
                thing_uri: "0",
#                 u"bnode": "1", # TODO: is the bnode color needed?
#                 u"literal": "2", # TODO: is the literal color needed?
                u"http://www.w3.org/2001/XMLSchema#string": "1" # default literal type
            }
            color_id = 2
        
        if discard_classes:
            all_classes = get_all_classes(rdf_graph)
        
        for node in nodes:
            if discard_classes:
                if node in all_classes:
                    # we ignore classes
                    # TODO: what about predicates and other ontology definitions?
                    continue
            u_node = unicode(node)
            if u_node not in uri_node_map:
                node_kind = type(node)
                node_colors = set()
#                 if node_kind is BNode:
#                     # add the bnode color
#                     node_colors.add(colors[u"bnode"])
                if node_kind in [BNode, URIRef]:
                    # add a color for each type of the node
                    types = list(get_node_types(rdf_graph, node))
                    if not types:
                        # if there are no types add base color
                        node_colors.add(colors[thing_uri])
                    for node_type in types:
                        node_type_raw = unicode(node_type)
                        if node_type_raw not in colors:
                            colors[node_type_raw] = str(color_id)
                            color_id += 1
                        node_colors.add(colors[node_type_raw])
                elif node_kind is Literal:
                    # add the literal color and the color for the datatype of the literal
#                     node_colors.add(colors[u"literal"])
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
                    node_colors.add(colors[thing_uri])
                nx_graph.add_node(node_id, labels=list(node_colors))
                uri_node_map[u_node] = node_id
                node_id += 1
        
        for s, p, o in triples:
            if p == RDF.type:
                # skip RDF.type edges
                continue
            if discard_classes:
                if s in all_classes or o in all_classes:
                    # skip edges from/to classes
                    continue
            s_id = uri_node_map[unicode(s)]
            o_id = uri_node_map[unicode(o)]
            p_raw = unicode(p)
            if p_raw not in colors:
                    colors[p_raw] = str(color_id)
                    color_id += 1
            nx_graph.add_edge(s_id, o_id, label=colors[p_raw])
    
    if return_colors:
        return nx_graph, uri_node_map, colors, color_id
    else:
        return nx_graph, uri_node_map

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

def extend_inferred_knowledge(in_files, out_file):
    '''Uses the RDFClosure reasoner to create
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
    convert_graph(options, destination=out_file)

def sparql_query(query, base_rdf_graph=None, sparql_endpoint="http://localhost:3030/ds/query", return_new_node_uris=False,
                 s_default=None, p_default=None, o_default=None):
    def to_rdflib_term(term_dict):
        term_type = term_dict[u'type']
        if term_type == u'uri':
            return rdflib.URIRef(term_dict[u'value'])
        elif term_type == u'literal':
            if u'xml:lang' in term_dict:
                return rdflib.Literal(term_dict[u'value'], lang=term_dict[u'xml:lang'])
            else:
                return rdflib.Literal(term_dict[u'value'])
        elif term_type == u'typed-literal':
            return rdflib.Literal(term_dict[u'value'], datatype=term_dict[u'datatype'])
        elif term_type == u'bnode':
            return rdflib.BNode(term_dict[u'value'])
        else:
            print "RDF term of unknown type:", term_dict
            exit(1)
    sparql = SPARQLWrapper(sparql_endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    rdf_data = sparql.query().convert()
    if base_rdf_graph:
        rdf_graph = base_rdf_graph
    else:
        rdf_graph = RDFGraph()
    
    if return_new_node_uris:
        new_node_uris = set()
    
    for triple in rdf_data[u"results"][u"bindings"]:
        if u's' in triple:
            s = to_rdflib_term(triple[u's'])
        else:
            s = rdflib.URIRef(s_default)
        
        if u'p' in triple:
            p = to_rdflib_term(triple[u'p'])
        else:
            p = rdflib.URIRef(p_default)
        
        if u'o' in triple:
            o = to_rdflib_term(triple[u'o'])
        else:
            o = rdflib.URIRef(o_default)
        
        rdf_graph.add((s, p, o))
        
        if return_new_node_uris:
            if u's' in triple:
                new_node_uris.add(triple[u's'][u'value'])
            if u'o' in triple:
                if triple[u'o'][u'type'] in [u'uri', u'bnode']:
                    new_node_uris.add(triple[u'o'][u'value'])
    
    if return_new_node_uris:
        return 0, rdf_graph, new_node_uris
    else:
        return 0, rdf_graph

def quary_r_ball(center_node_uri, r, edge_dir, sparql_endpoint="http://localhost:3030/ds/query", ignore_type_paths=True, include_types=True):
    '''Does the same as ivanov.graph.algorithms.r_ball but using an RDF graph and with a SPARQL query.
    :param center_node_uri: the center node of the r-ball
    :param r: radius of the r-ball (in hops)
    :param edge_dir: the direction of edges to be considered (0 - all edges, 1 - only outgoing, -1 - only incoming)
    :param sparql_endpoint: URL of the SPARQL end-point. Default is http://localhost:3030/ds/query (for Apache Jena Fuseki)
    :param ignore_type_paths: (default True) ignore all rdf:type edges when extracting the r-ball (rdf:type information
    can be extracted additionally if include_types=True)
    :param include_types: (default True) include the types of each node in the r-ball
    :return: the tuple (query_status, rdf_r_ball)
    '''
    def build_rball_query(center, max_depth, level = 0, direction_sequence = []):
        # recursively builds the query for extracting the r-ball
        query = u""

        if level > 0:
            query += u" UNION "
        
        if edge_dir >= 0:
            query += u"{{?s ?p ?o."
            if ignore_type_paths:
                filter_types = filter_type_paths(level)
            if level > 0:
                for i in range(0, level):
                    s = u""
                    o = u""
                    if direction_sequence[i]:
                        if i == 0:
                            s = center
                            o = u"?o0"
                        else:
                            if direction_sequence[i - 1]:
                                s = u"?o%d" % (i - 1)
                                o = u"?o%d" % i
                            else:
                                s = u"?s%d" % (i - 1)
                                o = u"?o%d" % i
                        if i == level - 1:
                            o = u"?s"
                    else:
                        if i == 0:
                            s = u"?s0"
                            o = center
                        else:
                            if direction_sequence[i - 1]:
                                s = u"?s%d" % i
                                o = u"?o%d" % (i - 1)
                            else:
                                s = u"?s%d" % i
                                o = u"?s%d" % (i - 1)
                        if i == level - 1:
                            s = u"?s"
                    
                    query += u" {0} ?p{1} {2}.".format(s, i, o)
                
                if ignore_type_paths:
                    query += u" FILTER({0})".format(filter_types)
            else:
                if ignore_type_paths:
                    query += u" FILTER(?s = {0} && {1})".format(center, filter_types)
                else:
                    query += u" FILTER(?s = {0})".format(center)
            query += u"}"
            if level < max_depth:
                query += build_rball_query(center, max_depth, level + 1, direction_sequence + [True])
            
            query += u"}"
        
        if edge_dir == 0:
            query += u" UNION "
        
        if edge_dir <= 0:
            query += u"{{?s ?p ?o."
            if ignore_type_paths:
                filter_types = filter_type_paths(level)
            if level > 0:
                for i in range(0, level):
                    s = u""
                    o = u""
                    if direction_sequence[i]:
                        if i == 0:
                            s = center
                            o = u"?o0"
                        else:
                            if direction_sequence[i - 1]:
                                s = u"?o%d" % (i - 1)
                                o = u"?o%d" % i
                            else:
                                s = u"?s%d" % (i - 1)
                                o = u"?o%d" % i
                        if i == level - 1:
                            o = u"?o"
                    else:
                        if i == 0:
                            s = u"?s0"
                            o = center
                        else:
                            if direction_sequence[i - 1]:
                                s = u"?s%d" % i
                                o = u"?o%d" % (i - 1)
                            else:
                                s = u"?s%d" % i
                                o = u"?s%d" % (i - 1)
                        if i == level - 1:
                            s = u"?o"
                    
                    query += u" {0} ?p{1} {2}.".format(s, i, o)
                
                if ignore_type_paths:   
                    query += u" FILTER({0})".format(filter_types)
            else:
                if ignore_type_paths:
                    query += u" FILTER(?o = {0} && {1})".format(center, filter_types)
                else:
                    query += u" FILTER(?o = {0})".format(center)
            query += u"}"
            if level < max_depth:
                query += build_rball_query(center, max_depth, level + 1, direction_sequence + [False])

            query += u"}"
        
        return query
    
    def filter_type_paths(level):
        conditions = []
        conditions.append(u"?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>")
        for i in range(0, level):
            conditions.append(u"?p{0} != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>".format(i))
        return u" && ".join(conditions)
    
    def build_extract_types_query(node_uris):
        query = u"SELECT DISTINCT ?s ?p ?o WHERE {"
        block_template = u"{{ ?s ?p ?o FILTER(?s = <{0}> && ?p = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>) }}"
        blocks = map(lambda uri: block_template.format(uri), node_uris)
        query += u" UNION ".join(blocks)
        query += u"}"
        return query
    
    query_list_prefix = u"SELECT DISTINCT ?s ?p ?o WHERE {"
    query_list = query_list_prefix + build_rball_query("<" + center_node_uri + ">", r - 1) + "}"
    if include_types:
        status, rdf_graph, node_uris = sparql_query(query_list, sparql_endpoint=sparql_endpoint, return_new_node_uris=True)
        node_uris.add(center_node_uri) # just in case the query result was empty
        node_uris = list(node_uris)
        batch_size = 100
        offset = 0
        for _ in range(len(node_uris) / batch_size + 2): # split in batches of 100 to make queries smaller
            offset_end = offset + batch_size
            node_uris_batch = node_uris[offset : offset_end]
            if node_uris_batch:
                extract_types_query = build_extract_types_query(node_uris_batch)
                status, rdf_graph = sparql_query(extract_types_query, base_rdf_graph=rdf_graph, sparql_endpoint=sparql_endpoint)
            offset = offset_end
    else:
        status, rdf_graph = sparql_query(query_list, sparql_endpoint=sparql_endpoint)
    
    return status, rdf_graph

def quary_2_in_ball(center_node_uri, sparql_endpoint="http://localhost:3030/ds/query"):
    def build_extract_types_query(node_uris):
        query = u"SELECT DISTINCT ?s ?p ?o WHERE {"
        block_template = u"{{ ?s ?p ?o FILTER(?s = <{0}> && ?p = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>) }}"
        blocks = map(lambda uri: block_template.format(uri), node_uris)
        query += u" UNION ".join(blocks)
        query += u"}"
        return query
    
    query = u"SELECT ?s ?p WHERE {{?s ?p <{0}> FILTER(?p != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)}}"
    
    # extract neighborhood around center
    status, rdf_graph, node_uris = sparql_query(query.format(center_node_uri), sparql_endpoint=sparql_endpoint, return_new_node_uris=True,
                                                o_default=center_node_uri)
    
    # extract neighborhood around neighbors of the center
    for node_uri in list(node_uris):
        status, rdf_graph, new_node_uris = sparql_query(query.format(node_uri), base_rdf_graph=rdf_graph, sparql_endpoint=sparql_endpoint,
                                                        return_new_node_uris=True, o_default=node_uri)
        node_uris |= new_node_uris
    
    node_uris.add(center_node_uri) # just in case the query result was empty
    
    node_uris = list(node_uris)
    batch_size = 100
    offset = 0
    for _ in range(len(node_uris) / batch_size + 2): # split in batches of 100 to make queries smaller
        offset_end = offset + batch_size
        node_uris_batch = node_uris[offset : offset_end]
        if node_uris_batch:
            extract_types_query = build_extract_types_query(node_uris_batch)
            status, rdf_graph = sparql_query(extract_types_query, base_rdf_graph=rdf_graph, sparql_endpoint=sparql_endpoint)
        offset = offset_end
    
    return status, rdf_graph
