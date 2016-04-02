'''
Created on Mar 18, 2016

@author: Ivan Ivanov
'''
from ivanov.graph import dataset_manager, rdf, nxext
from ivanov import helpers, inout

if __name__ == '__main__':
#     dataset = "mutagenicity-rdf"
#     in_files = helpers.datasets[dataset]["files"]
#     compounds_targets_file = helpers.datasets[dataset]["compounds_targets"]["sample-2"]
#     uri_prefix = "http://dl-learner.org/mutagenesis#"
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity_rdf/data_feature_shingles/"
#     dataset_manager.build_svmlight_chemical_data(in_files, 11, output_dir, True, compounds_targets_file, uri_prefix, shingles_type="features", accumulate_wl_shingles=False)
# #     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity_rdf/data_w_{0}/"
# #     for w in range(2, 21):
# #         dataset_manager.build_svmlight_chemical_data(in_files, 5, output_dir.format(w), format_rdf=True,
# #                                                      compounds_targets_file=compounds_targets_file, uri_prefix=uri_prefix,
# #                                                      shingles_type="w-shingles", window_size=w, accumulate_wl_shingles=False)
# # #     list(dataset_manager.prepare_rdf_chemical_data(in_files, compounds_targets_file, uri_prefix))

#     dataset = "mutagenicity"
#     in_files = helpers.datasets[dataset]["files"]
# #     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity/data/"
# #     dataset_manager.build_svmlight_chemical_data(in_files, 11, output_dir)
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity/data_w_{0}/"
#     for w in [5]: #range(1, 20):
#         dataset_manager.build_svmlight_chemical_data(in_files, 5, output_dir.format(w), shingles_type="w-shingles", window_size=w)
    
#     dataset = "nci-hiv"
#     in_files = helpers.datasets[dataset]["files"]
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/nci_hiv/data_w_{0}/"
#     for w in [5, 10, 20]: # range(5, 6):
#         dataset_manager.build_svmlight_chemical_data(in_files, 3, output_dir.format(w), shingles_type="w-shingles", window_size=w, fingerprints=True)
    
    output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/dbp_online/2_in_balls/"
    entries_file = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/dbpedia/dbpedia_ascii_resources_sample_10000"
    radius = 2
    edge_dir = -1
      
    # SPARQL end-points:
    # "http://dbpedia.org/sparql"
    # "http://localhost:3030/ds/query"
      
    nodes_count_distribution, type_distribution = dataset_manager.extract_rballs_from_rdf_server_using_entries_file(entries_file, output_dir, radius, edge_dir, sparql_endpoint="http://dbpedia.org/sparql")
    print nodes_count_distribution
    print type_distribution
    
#     def read_r_balls_database(r_balls_directory, r_balls_count):
#         for i in range(r_balls_count):
#             record = inout.load_from_file(r_balls_directory + "r_ball_{0}".format(i))
#             yield record
#      
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/data_1_in_balls/data_w_{0}/"
#     r_balls_directory = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_rdf/dbpedia/1_in_balls/"
#     for w in [5, 10]:
#         r_balls_database = read_r_balls_database(r_balls_directory, 10000)
#         dataset_manager.build_multilabel_svm_light_data_from_graph_database(r_balls_database, 4, output_dir.format(w), shingles_type="w-shingles",
#                 window_size=w, accumulate_wl_shingles=True, fingerprints=False)
