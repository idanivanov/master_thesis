'''
Created on Feb 4, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.hypergraph import Hypergraph
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
    
    current_graph = None
    current_properties = None
    with codecs.open(in_file, "r", "utf8") as fp:
        i = 0
        for line in fp:
            if i == 0:
                if line.startswith("$"): # EOF
                    break
                assert line.startswith("#")
                current_properties = map(lambda x: int(x), line.split(" ")[1:])
                current_graph = nx.Graph()
#                 if current_properties[0] > 10:
#                     break
            elif i == 1:
                nodes = line.split(" ")[:-1]
                assert len(nodes) == current_properties[2]
                for node_index, node_label in enumerate(nodes):
                    current_graph.add_node(node_index + 1, labels=[node_label])
            else:
                edges = line.split(" ")[:-1]
                edges = [edges[e : e + 3] for e in itertools.imap(lambda x: 3 * x, range(len(edges)/3))]
                assert len(edges) == current_properties[3]
                for edge in edges:
                    current_graph.add_edge(int(edge[0]), int(edge[1]), label=edge[2])
                
                ch_db_record = (current_properties[0], [Hypergraph(current_graph)], current_properties[1])
                chem_graph_database.append(ch_db_record)
                chem_props.append(current_properties)
            i = (i + 1) % 3
    
    return chem_graph_database, chem_props
