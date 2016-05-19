'''
Created on Mar 18, 2016

@author: Ivan Ivanov
'''
from ivanov.graph import dataset_manager, rdf, nxext
from ivanov import helpers, inout
from ivanov.graph.algorithms import arnborg_proskurowski

if __name__ == '__main__':
#     dataset = "mutagenicity-rdf"
#     in_files = helpers.datasets[dataset]["files"]
#     compounds_targets_file = helpers.datasets[dataset]["compounds_targets"]["sample-188"]
#     uri_prefix = "http://dl-learner.org/mutagenesis#"
# #     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity_rdf/data_feature_shingles/"
# #     dataset_manager.build_svmlight_chemical_data(in_files, 11, output_dir, True, compounds_targets_file, uri_prefix, shingles_type="features", accumulate_wl_shingles=False)
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity_rdf/data_w_shingles_accumulate/data_w_{0}/"
#     for w in range(2, 21):
#         dataset_manager.build_svmlight_chemical_data(in_files, 5, output_dir.format(w), format_rdf=True,
#                                                      compounds_targets_file=compounds_targets_file, uri_prefix=uri_prefix,
#                                                      shingles_type="w-shingles", window_size=w, accumulate_wl_shingles=True)
# #     list(dataset_manager.prepare_rdf_chemical_data(in_files, compounds_targets_file, uri_prefix))
    
#     dataset = "carcinogenesis-rdf-owl"
#     in_files = helpers.datasets[dataset]["files"]
#     compounds_targets_file = helpers.datasets[dataset]["compounds_targets"]["sample-1"]
#     uri_prefix = "http://dl-learner.org/carcinogenesis#"
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/carcinogenesis_rdf/data_w_shingles_accumulate/data_w_{0}/"
#     for w in range(2, 21):
#         dataset_manager.build_svmlight_chemical_data(in_files, 5, output_dir.format(w), format_rdf=True,
#                                                      compounds_targets_file=compounds_targets_file, uri_prefix=uri_prefix,
#                                                      shingles_type="w-shingles", window_size=w, accumulate_wl_shingles=True)
# #     list(dataset_manager.prepare_rdf_chemical_data(in_files, compounds_targets_file, uri_prefix))
    
#     dataset = "mutagenicity"
#     in_files = helpers.datasets[dataset]["files"]
# #     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity/data/"
# #     dataset_manager.build_svmlight_chemical_data(in_files, 11, output_dir)
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity/data_w_shingles_accumulate/data_w_{0}/"
#     for w in range(2, 21):
#         dataset_manager.build_svmlight_chemical_data(in_files, 5, output_dir.format(w), shingles_type="w-shingles", window_size=w,
#                                                      accumulate_wl_shingles=True)
    
#     dataset = "nci-hiv"
#     in_files = helpers.datasets[dataset]["files"]
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/nci_hiv/data_w_{0}/"
#     for w in [5, 10, 20]: # range(5, 6):
#         dataset_manager.build_svmlight_chemical_data(in_files, 3, output_dir.format(w), shingles_type="w-shingles", window_size=w, fingerprints=True)
    
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/3.8/1_all_balls/"
#     #entries_file = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/dbpedia/2015-10/dbpedia_bounded_in_degree_resources_sample_10000"
#     entries_file = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/dbpedia/3.8/dbpedia_sample_10000"
#     entries_count = 10000
#     radius = 1
#     edge_dir = 0
#           
#     # SPARQL end-points:
#     # "http://dbpedia.org/sparql"
#     # "http://localhost:3030/ds/query"
#     sparql_endpoint="http://localhost:3030/ds/query"
#      
#     nodes_count_distribution, type_distribution = dataset_manager.extract_rballs_from_rdf_server_using_entries_file(
#                                                     entries_file, output_dir, radius, edge_dir, sparql_endpoint=sparql_endpoint,
#                                                     entries_count_expected=entries_count)
#     with open("nc", "w") as f:
#         f.write(str(nodes_count_distribution))
#         f.write(str(type_distribution))
#     print "Done"

    def read_r_balls_database(r_balls_directory, r_balls_count):
        for i in range(r_balls_count):
            record = inout.load_from_file(r_balls_directory + "r_ball_{0}".format(i))
            yield record
         
    r_balls_directory = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/3.8/1_in_balls/"
    output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/3.8/data_1_in_balls/data_w_{0}/"
    wl_iterations = 4
    for w in [5, 10]:
        r_balls_database = read_r_balls_database(r_balls_directory, 10000)
        dataset_manager.build_multilabel_svm_light_data_from_graph_database(r_balls_database, wl_iterations, output_dir.format(w), shingles_type="w-shingles",
                window_size=w, accumulate_wl_shingles=True, fingerprints=False)
    
#     r_balls_database = read_r_balls_database(r_balls_directory, 10000)
#     with open("tw_1_in_balls", "w") as f:
#         for i, record in enumerate(r_balls_database):
#             r_id, r_graphs, _ = record
#             tw = arnborg_proskurowski.get_treewidth(r_graphs[0])
#             line = "{0} {1}\n".format(r_id, tw)
#             print i, line
#             f.write(line)
#     print "Done"
    
#     # SML-Bench stuff
#     dataset = "carcinogenesis-rdf-owl"
#     in_files = helpers.datasets[dataset]["files"]
#     positives_file = helpers.datasets[dataset]["positives-file"]
#     negatives_file = helpers.datasets[dataset]["negatives-file"]
#     wl_iterations = 5
#     window_size = 15
#     output_file_name = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/sml_bench/test"
#     dataset_manager.build_sml_bench_vectors_from_rdf_chemical_data(in_files, wl_iterations,
#                     output_file_name, positives_file, negatives_file, window_size=window_size)
