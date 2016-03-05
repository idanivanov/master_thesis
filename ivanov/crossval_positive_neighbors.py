'''
Created on Mar 4, 2016

@author: Ivan Ivanov
'''
from ivanov.learning.positive_neighbors import PositiveNeighbors
from ivanov.graph import dataset_manager
from ivanov import helpers
import numpy as np

if __name__ == '__main__':
    
#     path = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/mutagenicity/"
#     path = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/nci_hiv/"
    path = "/home/stud/ivanovi/Thesis/svm/nci_hiv/"
    
#     wl_props = helpers.svm_light_format_datasets["mutagenicity"]
    wl_props = helpers.svm_light_format_datasets["nci-hiv"]["A-vs-M"]
#     wl_props = helpers.svm_light_format_datasets["nci-hiv"]["AM-vs-I"]
#     wl_props = helpers.svm_light_format_datasets["nci-hiv"]["A-vs-I"]
    
    output_file = path + "positive_neighbors_A_vs_M"
    
    print "Start"
    
    with open(output_file, "w") as fl:
        for w in range(0, 12):
            records_count = wl_props["examples_count"]
            input_dimensions = wl_props["dim_wl_iter_{0}".format(w)]
            data_file = path + wl_props["file_template"].format(w)
            X, y = dataset_manager.read_svm_light_bool_data_to_sparse(data_file, records_count, input_dimensions)
            y = np.vectorize(lambda t: 1 if t == 2 else -1)(y) # Only for A_vs_M
#             y = np.vectorize(lambda t: 1 if t == 2 else t)(y) # Only for AM_vs_I and A_vs_I
            for n in range(1, 40):
                prediction = PositiveNeighbors.cross_validate(X, y, n_neighbors=n, folds_count=10, approximate=False)
                print w, n, prediction
                fl.write("{0}, {1}, {2}\n".format(w, n, prediction))
                fl.flush()
                if prediction == 1.:
                    break
    
    print "Done"
