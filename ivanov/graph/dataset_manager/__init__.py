'''
Created on Feb 4, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import feature_extraction,\
    shingle_extraction
from ivanov.graph.hypergraph import Hypergraph
from scipy.sparse import csr_matrix
import networkx as nx
import numpy as np
import itertools
import codecs

def read_chemical_compounts(in_file, process_compound_function=None):
    '''Read a dataset of chemical compound graphs (e.g. Mutagenicity).
    :param in_file: Input text file.
    :return: the tuple (g, p) where g is a graph database to be used in building
    a characteristic matrix and p is a list containing the properties of the
    graphs in the database.
    '''
    chem_graph_database = []
    
    current_graph = None
    current_properties = None
#     r = 0
    with codecs.open(in_file, "r", "utf8") as fp:
        i = 0
        for line in fp:
            if i == 0:
#                 r += 1
#                 print "Processing row:", r
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
                if process_compound_function:
                    process_compound_function(ch_db_record)
                yield ch_db_record
            i = (i + 1) % 3

def build_svmlight_chemical_data(in_file, wl_iterations, output_dir):
    files = []
    
    for i in range(wl_iterations + 1):
        files.append(open(output_dir + "svm_light_data_wl_{0}".format(i), "w"))
    
    shingle_id_map = {}
    state = {"wl_state": None, "next_shingle_id": 1}
    
    def process_compound(chem_record):
        print "Record ID: {0}, Target: {1}".format(chem_record[0], chem_record[2])
        fea_ext_iter = feature_extraction.extract_features_for_each_wl_iter(chem_record[1][0], wl_iterations, state["wl_state"])
        record_data_vector = set()
        for wl_it, new_features, state["wl_state"] in fea_ext_iter:
            for feature in new_features:
                shingles = shingle_extraction.extract_shingles(feature)
                for shingle in shingles:
                    if shingle not in shingle_id_map:
                        shingle_id_map[shingle] = state["next_shingle_id"]
                        state["next_shingle_id"] += 1
                    record_data_vector.add((shingle_id_map[shingle], 1))
            data_instance = (chem_record[2] if chem_record[2] > 0 else -1, sorted(record_data_vector, key=lambda x: x[0]))
            files[wl_it].write("{0} {1}\n".format(data_instance[0], " ".join(["{0}:{1}".format(f, v) for f, v in data_instance[1]])))
            files[wl_it].flush()
        
    chem_database = read_chemical_compounts(in_file, process_compound)
    
    for i, _ in enumerate(chem_database):
        print i
        
    for f in files:
        f.close()
    
    print "Done."

def read_svm_light_bool_data(in_file):
    with open(in_file) as in_f:
        for line in in_f:
            elem = line.split(" ")
            target = int(elem[0])
            props = []
            for e in elem[1:]:
                prop = e.split(":")
                if float(prop[1]) > 0.:
                    props.append(int(prop[0]))
            yield target, props

def read_svm_light_bool_data_to_sparse(in_file):
    data = read_svm_light_bool_data(in_file)
    
    y = []
    X_row = []
    X_col = []
    
    for i, (target, props) in enumerate(data):
        y.append(target)
        for prop in props:
            X_row.append(i)
            X_col.append(prop)
    
    X_data = np.full((len(X_row),), 1, dtype=np.int8)
    
    X = csr_matrix((X_data, (X_row, X_col)), dtype=np.int8)
    
    return X, np.array(y)
