'''
Created on Mar 18, 2016

@author: Ivan Ivanov
'''
from ivanov.graph import dataset_manager
from ivanov import helpers

if __name__ == '__main__':
#     dataset = "mutagenicity-rdf"
#     in_files = helpers.datasets[dataset]["files"]
#     compounds_targets_file = helpers.datasets[dataset]["compounds_targets"]["sample-2"]
#     uri_prefix = "http://dl-learner.org/mutagenesis#"
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity_rdf/data/"
#     dataset_manager.build_svmlight_chemical_data(in_files, 11, output_dir, True, compounds_targets_file, uri_prefix, w_shingles=True)
# #     list(dataset_manager.prepare_rdf_chemical_data(in_files, compounds_targets_file, uri_prefix))

#     dataset = "mutagenicity"
#     in_files = helpers.datasets[dataset]["files"]
#     output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/mutagenicity/data_w_{0}/"
#     for w in range(1, 20):
#         dataset_manager.build_svmlight_chemical_data(in_files, 5, output_dir.format(w), shingles_type="w-shingles", window_size=w)
    
    dataset = "nci-hiv"
    in_files = helpers.datasets[dataset]["files"]
    output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/nci_hiv/data_w_{0}/"
    for w in [5, 10, 20]: # range(5, 6):
        dataset_manager.build_svmlight_chemical_data(in_files, 3, output_dir.format(w), shingles_type="w-shingles", window_size=w)
