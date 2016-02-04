'''
Created on Feb 4, 2016

@author: Ivan Ivanov
'''
import networkx as nx
import itertools
import codecs

def read_chemical_compounts(in_file):
    '''Read a dataset of chemical compound graphs (e.g. Mutagenicity).
    :param in_file: Input text file.
    :return: the tuple (g, p) where g is a graph database to be used in building
    a characteristic matrix and p is a list containing the properties of the
    graphs in the database.
    '''
    chem_graph_database = []
    chem_props = [] # properties of the compounds indexed by their position in the chem_graph_database
    
    fd = codecs.open(in_file, "r", "utf8")
    current_graph = nx.Graph()
    current_properties = None
    i = 0
    for line in fd.readline():
        if i == 0:
            assert line.startswith("#")
            current_properties = line.split(" ")[1:]
        elif i == 1:
            nodes = line.split(" ")
            assert len(nodes) == current_properties[2]
            for node_id, node_label in enumerate(nodes):
                current_graph.add_node(node_id, labels=[node_label])
        else:
            edges = line.split(" ")
            edges = list(itertools.groupby(edges, key=lambda x: edges.index(x) - (edges.index(x) % 3)))
            assert len(edges) == current_properties[3]
            for _, edge in edges:
                edge = list(edge)
                current_graph.add_edge(edge[0], edge[1], label=edge[2])
            
            chem_graph_database.append([current_graph])
            chem_props.append(current_properties)
        i = (i + 1) % 3
    
    return chem_graph_database, chem_props
