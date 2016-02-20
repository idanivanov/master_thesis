'''
Created on Feb 17, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms import similar_graphs_mining, arnborg_proskurowski
from ivanov.graph import dataset_manager
from ivanov import helpers
# import svmlight as sl

dataset = "mutagenicity"
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

in_file = helpers.datasets[dataset]["files"][0]
dataset_manager.build_svmlight_chemical_data(in_file, 11, "../output_chem/svm/")
