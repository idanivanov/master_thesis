'''
Created on Feb 4, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import feature_extraction,\
    shingle_extraction
from ivanov.graph.algorithms import arnborg_proskurowski, weisfeiler_lehman
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import rdf, algorithms
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

def prepare_rdf_chemical_data(rdf_files, compounds_targets_file, uri_prefix, process_compound_function=None):
    def read_componds_and_targets():
        with open(compounds_targets_file, "r") as ct_file:
            for line in ct_file.readlines():
                if line.startswith("#"):
                    continue
                elif line.startswith("$"):
                    break
                else:
                    comp_id, target_label = tuple(line[:-1].split(" "))
                    yield unicode(comp_id), int(target_label)
    
    full_graph, uri_node_map, type_color_map = rdf.convert_rdf_to_nx_graph(rdf_files, return_colors=True)
    
    literal_colors = set()
    for rdf_type in type_color_map:
        # TODO: this condition is unsafe because it may remove not only literal colors
        if rdf_type.startswith(u"http://www.w3.org/2001/XMLSchema#"):
            literal_colors.add(type_color_map[rdf_type])
    
    for node in full_graph.nodes():
        # remove all literals
        if literal_colors & set(full_graph.node[node]["labels"]):
            full_graph.remove_node(node)
    
    for node in full_graph.nodes_iter():
        # remove the color of named individual type from all nodes where it occures
        named_indiv_color = type_color_map[u"http://www.w3.org/2002/07/owl#NamedIndividual"]
        if named_indiv_color in full_graph.node[node]["labels"]:
            full_graph.node[node]["labels"].remove(named_indiv_color)

    full_hypergraph = Hypergraph(full_graph)
    
    for comp_id, target_label in read_componds_and_targets():
        node_id = u"n_{0}".format(uri_node_map[uri_prefix + comp_id])
        comp_neighborhood_hypergraph = algorithms.r_ball_hyper(full_hypergraph, node_id, 2, 0)
        comp_neighborhood_hypergraph.safe_remove_node(node_id) # remove self
        for node in comp_neighborhood_hypergraph.nodes_iter():
            # remove isolated nodes
            if len(comp_neighborhood_hypergraph.neighbors(node)) == 0:
                comp_neighborhood_hypergraph.safe_remove_node(node)
#         # get the immediate neighbors of the compound node in a separate graph
#         r1_ball = algorithms.r_ball_hyper(full_hypergraph, node_id, 1, 0)
        ch_db_record = (comp_id, [comp_neighborhood_hypergraph], target_label)
        if process_compound_function:
            process_compound_function(ch_db_record)
        yield ch_db_record

def build_svmlight_chemical_data(in_files, wl_iterations, output_dir, format_rdf=False, compounds_targets_file=None,
                                 uri_prefix=None, shingles_type="features", window_size=5, accumulate_wl_shingles=True):
    if format_rdf:
        assert type(in_files) is list
        assert bool(compounds_targets_file)
        assert bool(uri_prefix)
    else:
        if type(in_files) is list:
            in_files = in_files[0]
    
    files = []
    
    for i in range(wl_iterations + 1):
        files.append(open(output_dir + "svm_light_data_wl_{0}".format(i), "w"))
    
    shingle_id_map = {}
    state = {"wl_state": None}
    if accumulate_wl_shingles:
        state["next_shingle_id"] = 1
    else:
        for i in range(wl_iterations + 1):
            state["wl_{0}_next_shingle_id".format(i)] = 1
    
    sh_type = 0 if shingles_type == "all" else -1 if shingles_type == "w-shingles" else 1 # default "features"
    
    def process_compound(chem_record):
        def process_shingles(shingles, record_data_vector, wl_it):
            next_shingle_id_key = "next_shingle_id" if accumulate_wl_shingles else "wl_{0}_next_shingle_id".format(wl_it)
            for shingle in shingles:
                if shingle not in shingle_id_map:
                    shingle_id_map[shingle] = state[next_shingle_id_key]
                    state[next_shingle_id_key] += 1
                record_data_vector.add((shingle_id_map[shingle], 1))
        
        print "Record ID: {0}, Target: {1}, Window-Size: {2}".format(chem_record[0], chem_record[2], window_size)
        record_data_wl_vectors = {i: set() for i in range(wl_iterations + 1)}

        for record_graph in chem_record[1]:
            if sh_type >= 0:
                if accumulate_wl_shingles:
                    record_data_vector = set()
                fea_ext_iter = feature_extraction.extract_features_for_each_wl_iter(record_graph, wl_iterations, state["wl_state"])
                for wl_it, new_features, state["wl_state"] in fea_ext_iter:
                    if not accumulate_wl_shingles:
                        record_data_vector = set()
                    for feature in new_features:
                        shingles = shingle_extraction.extract_shingles(feature)
                        process_shingles(shingles, record_data_vector, wl_it)
                    record_data_wl_vectors[wl_it] |= record_data_vector
            
            if sh_type <= 0:
                # TODO: should we exclude records with tree-width > 3?
                if accumulate_wl_shingles:
                    record_data_vector = set()
                w_shingles_ext_iter = shingle_extraction.extract_w_shingles_for_each_wl_iter(record_graph, wl_iterations, state["wl_state"], window_size=window_size)
                for wl_it, new_w_shingles, state["wl_state"] in w_shingles_ext_iter:
                    if not accumulate_wl_shingles:
                        record_data_vector = set()
                    process_shingles(new_w_shingles, record_data_vector, wl_it)
                    record_data_wl_vectors[wl_it] |= record_data_vector
        
        for wl_it in range(wl_iterations + 1):
            data_instance = (chem_record[2] if chem_record[2] > 0 else -1, sorted(record_data_wl_vectors[wl_it], key=lambda x: x[0]))
            files[wl_it].write("{0} {1}\n".format(data_instance[0], " ".join(["{0}:{1}".format(f, v) for f, v in data_instance[1]])))
            files[wl_it].flush()
    
    if format_rdf:
        chem_database = prepare_rdf_chemical_data(in_files, compounds_targets_file, uri_prefix, process_compound)
    else:
        chem_database = read_chemical_compounts(in_files, process_compound)
    
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
