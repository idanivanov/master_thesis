'''
Created on Mar 8, 2016

@author: Ivan Ivanov
'''

from ivanov.graph import dataset_manager
from sklearn import neighbors
from ivanov import helpers
import numpy as np
import itertools

def get_positive_neighbors_counts(X, y, k=None, radius=None, positive_label=1):
    assert bool(k) ^ bool(radius)
    
    if k:
        assert type(k) is int
        nn = neighbors.NearestNeighbors(n_neighbors=k + 1, algorithm="auto").fit(X)
    else:
        assert type(radius) is float
        nn = neighbors.NearestNeighbors(radius=radius, algorithm="auto").fit(X)
    pos_X_indices = np.where(y == positive_label)[0]
    positive_X = X[pos_X_indices]
    if k:
        neigh = nn.kneighbors(positive_X, return_distance=False)
    else:
        neigh = nn.radius_neighbors(positive_X, return_distance=False)
    neigh = neigh[:, 1:] # remove self from neighbors
    neigh_targets = np.vectorize(lambda x: y[x])(neigh)
    pos_neigh_counts = np.sum(neigh_targets == positive_label, axis=1)
    avg_pos_neigh_count = np.average(pos_neigh_counts)
    return itertools.izip(pos_X_indices, pos_neigh_counts), avg_pos_neigh_count

def arrange_results(models):
    models.sort(key=lambda x: (x["wl_iterations"], x["k"]))
    max_k = max(map(lambda x: x["k"], models))
    filler = " & "
    arranged_str = ""
    new_line = True
    for m in models:
        if new_line:
            arranged_str += "\\num{{{0}}}{1}".format(m["wl_iterations"], filler)
            new_line = False
        arranged_str += "\\num{{{0}}}".format(m["avg_count_prop"])
        if m["k"] == max_k:
            arranged_str += "\\\\\n"
            new_line = True
        else:
            arranged_str += filler
    
    return arranged_str

if __name__ == '__main__':
    
#     path = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/mutagenicity/"
    path = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/nci_hiv/"
#     path = "/home/stud/ivanovi/Thesis/svm/nci_hiv/"
    
#     wl_props = helpers.svm_light_format_datasets["mutagenicity"]
#     wl_props = helpers.svm_light_format_datasets["nci-hiv"]["A-vs-M"]
#     wl_props = helpers.svm_light_format_datasets["nci-hiv"]["AM-vs-I"]
    wl_props = helpers.svm_light_format_datasets["nci-hiv"]["A-vs-I"]
    
    output_file = path + "pos_neigh_count_A_vs_I"
    
    print "Start"
    
    with open(output_file, "w") as fl:
        for w in range(0, 12):
            data_file = path + wl_props["file_template"].format(w)
            X, y = dataset_manager.read_svm_light_bool_data_to_sparse(data_file)
#             y = np.vectorize(lambda t: 1 if t == 2 else -1)(y) # Only for A_vs_M
            y = np.vectorize(lambda t: 1 if t == 2 else t)(y) # Only for AM_vs_I and A_vs_I
#             for k in [1, 5, 10, 50, 100, 500, 1000, 1500]:
            for k in [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]:
                counts, avg_count = get_positive_neighbors_counts(X, y, k)
                model = {"wl_iterations": w, "k": k, "avg_count": avg_count, "avg_count_prop": avg_count / k}
                print model
                fl.write("{0},\n".format(model))
                fl.flush()
    
    print "Done."
