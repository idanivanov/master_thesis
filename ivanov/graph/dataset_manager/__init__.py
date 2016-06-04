'''
Created on Feb 4, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import feature_extraction,\
    shingle_extraction, fingerprint
from ivanov.graph.algorithms import arnborg_proskurowski, weisfeiler_lehman
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import rdf, algorithms
from scipy.sparse import csr_matrix
from ivanov import inout
import networkx as nx
import numpy as np
import itertools
import codecs
import time
import json

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

def prepare_rdf_chemical_data(rdf_files, compounds_targets_file, uri_prefix, process_compound_function=None,
                              compounds_and_targets=None, sort_rdf_nodes_before_processing=False,
                              rdf_colors_state=None):
    def read_compounds_and_targets():
        with open(compounds_targets_file, "r") as ct_file:
            for line in ct_file.readlines():
                if line.startswith("#"):
                    continue
                elif line.startswith("$"):
                    break
                else:
                    comp_id, target_label = tuple(line[:-1].split(" "))
                    yield unicode(comp_id), int(target_label)
    
    def chem_database_generator(full_graph, uri_node_map, type_color_map, compounds_and_targets):
        literal_colors = set()
        for rdf_type in type_color_map:
            # TODO: this condition is unsafe because it may remove not only literal colors
            if rdf_type.startswith(u"http://www.w3.org/2001/XMLSchema#"):
                literal_colors.add(type_color_map[rdf_type])
        
        for node in full_graph.nodes():
            # remove all literals
            if literal_colors & set(full_graph.node[node]["labels"]):
                full_graph.remove_node(node)
        
        # remove the color of named individual type from all nodes where it occurs
        named_indiv_uri = u"http://www.w3.org/2002/07/owl#NamedIndividual"
        if named_indiv_uri in type_color_map:
            named_indiv_color = type_color_map[named_indiv_uri]
            for node in full_graph.nodes_iter():
                if named_indiv_color in full_graph.node[node]["labels"]:
                    full_graph.node[node]["labels"].remove(named_indiv_color)
    
        full_hypergraph = Hypergraph(full_graph)
        
        if not compounds_and_targets:
            compounds_and_targets = read_compounds_and_targets()
        
        for comp_id, target_label in compounds_and_targets:
            node_id = u"n_{0}".format(uri_node_map[uri_prefix + comp_id])
            comp_neighborhood_hypergraph = algorithms.r_ball_hyper(full_hypergraph, node_id, 2, 0)
            comp_neighborhood_hypergraph.safe_remove_node(node_id) # remove self
            for node in list(comp_neighborhood_hypergraph.nodes_iter()):
                # remove isolated nodes
                if len(comp_neighborhood_hypergraph.neighbors(node)) == 0:
                    comp_neighborhood_hypergraph.safe_remove_node(node)
    #         # get the immediate neighbors of the compound node in a separate graph
    #         r1_ball = algorithms.r_ball_hyper(full_hypergraph, node_id, 1, 0)
            ch_db_record = (comp_id, [comp_neighborhood_hypergraph], target_label)
            if process_compound_function:
                process_compound_function(ch_db_record)
            yield ch_db_record
    
    if rdf_colors_state:
        rdf_base_colors = rdf_colors_state['colors']
        rdf_next_color_id = rdf_colors_state['next_color_id']
    else:
        rdf_base_colors = None
        rdf_next_color_id = None
    
    full_graph, uri_node_map, type_color_map, next_color_id = rdf.convert_rdf_to_nx_graph(rdf_files, return_colors=True,
                                                                                          test_mode=sort_rdf_nodes_before_processing,
                                                                                          base_colors=rdf_base_colors, next_color_id=rdf_next_color_id)
    
    chem_database = chem_database_generator(full_graph, uri_node_map, type_color_map, compounds_and_targets)
    new_rdf_colors_state = {'colors': type_color_map, 'next_color_id': next_color_id}
    
    return chem_database, new_rdf_colors_state

def process_record(record, wl_iterations, state, binary_target_labels=True, shingles_type="no-shingles", window_size=5, accumulate_wl_shingles=True, fingerprints=True, save_just_last_wl_it=False):
    def get_sh_type(shingles_type):
        if shingles_type == 'all':
            # includes both w-shingles and features
            return 3
        elif shingles_type == 'w-shingles':
            return 2
        elif shingles_type == 'features':
            return 1
        else: # default 'no-shingles', which means that the whole canonical representations will be returned
            return 0
    
    sh_type = get_sh_type(shingles_type)
    files = state["files"]
    wl_state = state["wl_state"]
    shingle_id_map = state["shingle_id_map"]
    
    def process_shingles(shingles, record_data_vector, wl_it):
        next_shingle_id_key = "next_shingle_id" if accumulate_wl_shingles else "wl_{0}_next_shingle_id".format(wl_it)
        if not fingerprints:
            for shingle in shingles:
                if shingle not in shingle_id_map:
                    shingle_id_map[shingle] = wl_state[next_shingle_id_key]
                    wl_state[next_shingle_id_key] += 1
                record_data_vector.add((shingle_id_map[shingle], 1))
        else:
            shingle_ids = set(fingerprint.get_fingerprints(shingles, size=24))
            record_data_vector |= set(map(lambda shingle_id: (shingle_id, 1), shingle_ids))
    
    if sh_type < 2:
        print "Record ID: {0}, Target: {1}".format(record[0], record[2])
    else:
        print "Record ID: {0}, Target: {1}, Window-Size: {2}".format(record[0], record[2], window_size)
    
    if sh_type != 0:
        record_data_wl_vectors = {i: set() for i in range(wl_iterations + 1)}
    else: # for 'no-shingles'
        record_canon_repr = [] # a list containing the canonical representations for each WL iteration

    for record_graph in record[1]:
        if sh_type == 1 or sh_type == 3:
            # for 'features' or 'all'
            if accumulate_wl_shingles:
                record_data_vector = set()
            fea_ext_iter = feature_extraction.extract_features_for_each_wl_iter(record_graph, wl_iterations, wl_state["wl_state"])
            for wl_it, new_features, wl_state["wl_state"] in fea_ext_iter:
                if not accumulate_wl_shingles:
                    record_data_vector = set()
                for feature in new_features:
                    shingles = shingle_extraction.extract_shingles(feature)
                    process_shingles(shingles, record_data_vector, wl_it)
                record_data_wl_vectors[wl_it] |= record_data_vector
        
        elif sh_type == 2 or sh_type == 3:
            # for 'w-shingles' and 'all'
            # TODO: should we exclude records with tree-width > 3?
            if accumulate_wl_shingles:
                record_data_vector = set()
            w_shingles_ext_iter = shingle_extraction.extract_w_shingles_for_each_wl_iter(record_graph, wl_iterations, wl_state["wl_state"], window_size=window_size)
            for wl_it, new_w_shingles, wl_state["wl_state"] in w_shingles_ext_iter:
                if not accumulate_wl_shingles:
                    record_data_vector = set()
                process_shingles(new_w_shingles, record_data_vector, wl_it)
                record_data_wl_vectors[wl_it] |= record_data_vector
        
        elif sh_type == 0:
            # for 'no-shingles'
            record_canon_representations_iter = shingle_extraction.extract_canon_repr_for_each_wl_iter(record_graph, wl_iterations, wl_state["wl_state"])
            for _, canon_repr, wl_state["wl_state"] in record_canon_representations_iter:
                # just collect the canonical representations for each WL iteration
                record_canon_repr.append('"' + canon_repr + '"')
    
    for wl_it in range(wl_iterations + 1):
        if sh_type != 0:
            if binary_target_labels:
                data_instance = (record[2] if record[2] > 0 else -1, sorted(record_data_wl_vectors[wl_it], key=lambda x: x[0]))
            else:
                data_instance = (",".join(record[2]), sorted(record_data_wl_vectors[wl_it], key=lambda x: x[0]))
        
            if not save_just_last_wl_it:
                files[wl_it].write("{0} {1}\n".format(data_instance[0], " ".join(["{0}:{1}".format(f, v) for f, v in data_instance[1]])))
                files[wl_it].flush()
        
        else: # for 'no-shingles'
            if binary_target_labels:
                target = record[2] if record[2] > 0 else -1
            else:
                target = ",".join(record[2])
            data = '[' + ','.join(record_canon_repr[:wl_it + 1]) + ']'
            
            if not save_just_last_wl_it:
                files[wl_it].write("{0} {1}\n".format(target, data))
                files[wl_it].flush()
    
    if save_just_last_wl_it:
        files[0].write("{0} {1}\n".format(data_instance[0], " ".join(["{0}:{1}".format(f, v) for f, v in data_instance[1]])))
        files[0].flush()

def build_svmlight_chemical_data(in_files, wl_iterations, output_dir, format_rdf=False, compounds_targets_file=None, uri_prefix=None,
                                 shingles_type="features", window_size=5, accumulate_wl_shingles=True, fingerprints=False,
                                 sort_rdf_nodes_before_processing=True, state_input_file=None, state_output_file=None):
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
    
    if state_input_file:
        state = inout.load_from_file(state_input_file)
        state['files'] = files
    else:
        wl_state = {"wl_state": None}
        shingle_id_map = {}
        if not fingerprints:
            if accumulate_wl_shingles:
                wl_state["next_shingle_id"] = 1
            else:
                for i in range(wl_iterations + 1):
                    wl_state["wl_{0}_next_shingle_id".format(i)] = 1
        
        state = {
            "files": files,
            "wl_state": wl_state,
            "shingle_id_map": shingle_id_map,
            "rdf_colors": {'colors': None, 'next_color_id': None}
        }
    
    def process_compound(chem_record):
        process_record(chem_record, wl_iterations, state, binary_target_labels=True,
                       shingles_type=shingles_type, window_size=window_size, accumulate_wl_shingles=accumulate_wl_shingles,
                       fingerprints=fingerprints)
    
    if format_rdf:
        chem_database, state['rdf_colors'] = prepare_rdf_chemical_data(in_files, compounds_targets_file, uri_prefix, process_compound,
                                                  sort_rdf_nodes_before_processing=sort_rdf_nodes_before_processing,
                                                  rdf_colors_state=state['rdf_colors'])
    else:
        chem_database = read_chemical_compounts(in_files, process_compound)
    
    for i, _ in enumerate(chem_database):
        print i
        
    for f in files:
        f.close()
    del state['files']
    
    if state_output_file:
        inout.save_to_file(state, state_output_file)
    
    print "Done."

def build_sml_bench_vectors_from_rdf_chemical_data(in_files, wl_iterations, output_file_name, positives_file, negatives_file, uri_prefix="",
                                                   shingles_type="w-shingles", window_size=5, accumulate_wl_shingles=True, fingerprints=False,
                                                   sort_rdf_nodes_before_processing=True):
    '''Extracts shingles of the records from a chemical data-set and saves them
    to an output file in a sparse binary vector format which is compatible
    with SVMlight and other implementations of SVM. Exactly one file is saved
    for the defined parameters of the shingle extraction.
    '''
    assert type(in_files) is list
    
    def read_compounds_and_targets():
        with open(negatives_file, "r") as neg_file:
            for line in neg_file.readlines():
                if line.startswith("$"):
                    break
                if not line.startswith("#"):
                    yield unicode(line[:-1]), -1
        with open(positives_file, "r") as pos_file:
            for line in pos_file.readlines():
                if line.startswith("$"):
                    break
                if not line.startswith("#"):
                    yield unicode(line[:-1]), 1
    
    out_file = open(output_file_name, "w")
    
    wl_state = {"wl_state": None}
    shingle_id_map = {}
    if not fingerprints:
        if accumulate_wl_shingles:
            wl_state["next_shingle_id"] = 1
        else:
            for i in range(wl_iterations + 1):
                wl_state["wl_{0}_next_shingle_id".format(i)] = 1
    
    state = {
        "files": [out_file],
        "wl_state": wl_state,
        "shingle_id_map": shingle_id_map
    }
    
    def process_compound(chem_record):
        process_record(chem_record, wl_iterations, state, binary_target_labels=True,
                       shingles_type=shingles_type, window_size=window_size, accumulate_wl_shingles=accumulate_wl_shingles,
                       fingerprints=fingerprints, save_just_last_wl_it=True)
    
    chem_database = prepare_rdf_chemical_data(in_files, None, uri_prefix, process_compound, read_compounds_and_targets(),
                                              sort_rdf_nodes_before_processing=sort_rdf_nodes_before_processing)
    
    for i, _ in enumerate(chem_database):
        print i
        
    out_file.close()
    
    print "Done."

def extract_rballs_from_rdf_server_using_entries_file(entries_file, output_dir, r, edge_dir, sparql_endpoint="http://localhost:3030/ds/query",
                                                      entries_count_expected=-1, sort_rdf_nodes_before_processing=True):
    def read_entries(nodes_in_file):
        with open(nodes_in_file) as in_fl:
            for line in in_fl.readlines():
                if line.startswith("#"):
                    continue
                yield line[:-1] # remove new line character from end
    
    entries = read_entries(entries_file)
    return extract_rballs_from_rdf_server(entries, output_dir, r, edge_dir, sparql_endpoint, entries_count_expected, sort_rdf_nodes_before_processing)

def extract_rballs_from_rdf_server(entries, output_dir, r, edge_dir, sparql_endpoint="http://localhost:3030/ds/query",
                                   entries_count_expected=-1, sort_rdf_nodes_before_processing=True):
    '''Extract r-balls around the given entry nodes from the graph on the server using SPARQL queries.
    :param entries: the entry nodes (resources, URI/IRIs) which will serve as center nodes of the r-balls
    :param output_dir: the directory for writing the output files
    :param r: radius of the r-balls
    :param edge_dir: the direction of edges to be considered (0 - all edges, 1 - only outgoing, -1 - only incoming)
    :param sparql_endpoint: URL of the SPARQL end-point. Default is http://localhost:3030/ds/query (for Apache Jena Fuseki)
    :param entries_count_expected: Expected number of entries to process.
    :param sort_rdf_nodes_before_processing: Used to yield the same colors in multiple runs. 
    '''
    colors = None
    next_color_id = None
    
    nodes_count_distribution = {}
    type_distribution = {}
    def update_stats(nodes_count, target_labels, colors):
        def get_target_uri_map():
            target_uri_map = {}
            for uri in colors:
                if colors[uri] in target_labels:
                    target_uri_map[colors[uri]] = uri
                    if len(target_uri_map) == len(target_labels):
                        break
            return target_uri_map
        
        if nodes_count not in nodes_count_distribution:
            nodes_count_distribution[nodes_count] = 0
        nodes_count_distribution[nodes_count] += 1
        
        target_uri_map = get_target_uri_map()
        for target in target_uri_map:
            type_uri = target_uri_map[target]
            if type_uri not in type_distribution:
                type_distribution[type_uri] = 0
            type_distribution[type_uri] += 1
    
    start_time = time.time()
    
    for i, entry_uri in enumerate(entries):
#         # TODO: specific case of 2-in-balls
#         query_status, rdf_r_ball = rdf.quary_2_in_ball(entry_uri, sparql_endpoint)
        query_status, rdf_r_ball = rdf.quary_r_ball(entry_uri, r, edge_dir, sparql_endpoint, ignore_type_paths=True, include_types=True)
        assert not query_status
        r_ball, uri_nodes_map, colors, next_color_id = rdf.convert_rdf_graph_to_nx_graph(rdf_r_ball, test_mode=sort_rdf_nodes_before_processing,
                                                                                         return_colors=True, base_colors=colors, next_color_id=next_color_id)
        if entry_uri not in uri_nodes_map:
            # in case the r-ball is empty
            node_id = 0
            r_ball.add_node(node_id, labels=["0"])
            uri_nodes_map[entry_uri] = node_id
        
        center_node = uri_nodes_map[entry_uri]
        target_labels = list(r_ball.node[center_node]["labels"])
        # Make he center node of color 0 (owl:Thing)
        # The original colors of the center node serve as target labels of the r-ball
        r_ball.node[center_node]["labels"] = ["0"]
        hyper_r_ball = Hypergraph(r_ball)
        nodes_count = r_ball.number_of_nodes()
        if i % 10 == 0: # print every 100 records
            elapsed_time = time.time() - start_time
            if entries_count_expected == -1 or i == 0:
                time_est = "Elapsed time: {0:.2f}s".format(elapsed_time)
            else:
                time_left = (elapsed_time / i) * (entries_count_expected - i) 
                time_est = "Time left: {0:.2f}s".format(time_left)
            print i, time_est, nodes_count, entry_uri, target_labels
        update_stats(nodes_count, target_labels, colors)
        graph_database_record = (entry_uri, [hyper_r_ball], target_labels)
        inout.save_to_file(graph_database_record, output_dir + "r_ball_{0}".format(i))
    
    return nodes_count_distribution, type_distribution

def build_multilabel_svm_light_data_from_graph_database(graph_database, wl_iterations, output_dir, shingles_type="features",
                                                        window_size=5, accumulate_wl_shingles=True, fingerprints=False):
    files = []
    
    for i in range(wl_iterations + 1):
        files.append(open(output_dir + "multilabel_svm_light_data_wl_{0}".format(i), "w"))
    
    wl_state = {"wl_state": None}
    shingle_id_map = {}
    if not fingerprints:
        if accumulate_wl_shingles:
            wl_state["next_shingle_id"] = 1
        else:
            for i in range(wl_iterations + 1):
                wl_state["wl_{0}_next_shingle_id".format(i)] = 1
    
    state = {
        "files": files,
        "wl_state": wl_state,
        "shingle_id_map": shingle_id_map
    }
    
    for i, record in enumerate(graph_database):
        print i
        process_record(record, wl_iterations, state, binary_target_labels=False,
                       shingles_type=shingles_type, window_size=window_size, accumulate_wl_shingles=accumulate_wl_shingles,
                       fingerprints=fingerprints)

def read_svm_light_bool_data(in_file):
    with open(in_file) as in_f:
        for line in in_f:
            elem = line.split(" ")
            targets = map(lambda l: int(l), elem[0].split(","))
            props = []
            for e in elem[1:]:
                if e == "\n":
                    break
                prop = e.split(":")
                if float(prop[1]) > 0.:
                    props.append(int(prop[0]))
            yield targets, props

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

def read_canonical_representations_data(in_file):
    with open(in_file) as in_f:
        for line in in_f:
            elem = line.split(" ")
            assert len(elem) == 2
            targets = map(lambda l: int(l), elem[0].split(","))
            canon_representations = json.loads(elem[1])
            yield targets, canon_representations
