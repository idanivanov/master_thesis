'''
Created on Feb 17, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms import similar_graphs_mining, arnborg_proskurowski
from ivanov.graph import dataset_manager
from ivanov import helpers
import svmlight as sl

import codecs
import networkx as nx
import itertools
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph.algorithms.similar_graphs_mining import feature_extraction,\
    shingle_extraction

dataset = "nci-hiv"
wl_iter_range = range(0, 12)
output_dir = "../output_chem/svm_test/"
crossval_folds = 10

# if __name__ == '__main__':
#     in_file = helpers.datasets[dataset]["files"][0]
#     graph_database, chem_props = dataset_manager.read_chemical_compounts(in_file)
#     
#     for wl_iterations in wl_iter_range:
#         print wl_iterations
#         svm_data = similar_graphs_mining.build_svmlight_data(graph_database, wl_iterations, "hiv_data_wl_{0}".format(wl_iterations))
# #         fold_size = len(graph_database) / crossval_folds
# #         total_accuracy = 0.
# #         offset = 0
# #         offset_end = fold_size
# #         for _ in range(crossval_folds):
# #             training_data = svm_data[:offset]
# #             training_data += svm_data[offset_end:]
# #             test_data = svm_data[offset : offset_end]
# #             model = sl.learn(training_data, type='classification', verbosity=0)
# #             predictions = sl.classify(model, test_data)
# #             correct = [predictions[i] == test_data[i][0] for i in range(len(predictions))]
# #             accuracy = float(len(filter(lambda x: x, correct))) / float(len(correct))
# #             total_accuracy += accuracy
# #             
# #             offset = offset_end
# #             offset_end += fold_size
# #         
# #         total_accuracy /= float(crossval_folds)
# #         print wl_iterations, total_accuracy
#     print "done"

files = []

for i in wl_iter_range:
    files.append(open("hiv_data_wl_{0}".format(i), "w"))


shingle_id_map = {}
state = {"wl_state": None, "next_shingle_id": 1}

def process_compound(chem_record):
    print chem_record[0], chem_record[2]
    fea_ext_iter = feature_extraction.extract_features_for_each_wl_iter(chem_record[1][0], wl_iter_range[-1], state["wl_state"])
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
    
in_file = helpers.datasets[dataset]["files"][0]
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
            process_compound(ch_db_record)
        i = (i + 1) % 3

for f in files:
    f.close()
