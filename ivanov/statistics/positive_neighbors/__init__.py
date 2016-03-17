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
        neigh = neigh[:, 1:] # remove self from neighbors
        neigh_targets = np.vectorize(lambda x: y[x])(neigh)
        neigh_shape = np.shape(neigh_targets)
        neigh_counts = np.full((neigh_shape[0],), np.float(neigh_shape[1]), dtype=np.float)
        pos_neigh_counts = np.sum(neigh_targets == positive_label, axis=1)
    else:
        neigh = nn.radius_neighbors(positive_X, return_distance=False)
        neigh = map(lambda tup: np.delete(tup[1], np.where(tup[1] == pos_X_indices[tup[0]])), enumerate(neigh)) # remove self from neighbors
        neigh_targets = map(lambda n: np.vectorize(lambda x: y[x])(n) if n.size else np.array([]), neigh)
        neigh_counts = np.array(map(lambda n: np.float(np.shape(n)[0]), neigh_targets), dtype=np.float)
        pos_neigh_counts = np.array(map(lambda n: np.sum(n == positive_label), neigh_targets))
    
    pos_neigh_proportions = pos_neigh_counts / neigh_counts
    pos_neigh_proportions = np.nan_to_num(pos_neigh_proportions) # empty neighborhoods to 0
    
#     # remove empty neighborhoods 
#     not_nan_indices = ~np.isnan(pos_neigh_proportions)
#     avg_pos_neigh_count = np.average(pos_neigh_counts[not_nan_indices])
#     avg_pos_neigh_prop = np.average(pos_neigh_proportions[not_nan_indices])
    
    avg_pos_neigh_count = np.average(pos_neigh_counts)
    avg_pos_neigh_prop = np.average(pos_neigh_proportions)
    return itertools.izip(pos_X_indices, pos_neigh_counts, pos_neigh_proportions), avg_pos_neigh_count, avg_pos_neigh_prop

def arrange_results(models, param_is_k):
    if type(models) is not list:
        models = list(models)
    
    param_name = "k" if param_is_k else "radius"
    models.sort(key=lambda x: (x["wl_iterations"], x[param_name]))
    max_param = max(map(lambda x: x[param_name], models))
    filler = " & "
    arranged_str = ""
    new_line = True
    for m in models:
        if new_line:
            arranged_str += "\\num{{{0}}}{1}".format(m["wl_iterations"], filler)
            new_line = False
        arranged_str += "\\num{{{0}}}".format(m["avg_prop"])
        if m[param_name] == max_param:
            arranged_str += "\\\\\n"
            new_line = True
        else:
            arranged_str += filler
    
    return arranged_str

def get_positive_neighbors_models(in_svm_data_file_template, output_file, wl_iter_range,
                                       k_range=None, radius_range=None, override_tergets_function=None):
    assert bool(k_range) ^ bool(radius_range)
    
    def compute_model(X, y, param, param_is_k):
        _, avg_count, avg_prop = get_positive_neighbors_counts(X, y, k=param if param_is_k else None, radius=None if param_is_k else param)
        model = {"wl_iterations": w, "avg_count": avg_count, "avg_prop": avg_prop}
        if param_is_k:
            model["k"] = param
        else:
            model["radius"] = param
        return model
    
    param_range = k_range if k_range else radius_range
    param_is_k = bool(k_range)
    
    with open(output_file, "w") as fl:
        for w in wl_iter_range:
            data_file = in_svm_data_file_template.format(w)
            X, y = dataset_manager.read_svm_light_bool_data_to_sparse(data_file)
            if override_tergets_function:
                y = override_tergets_function(y)
            for param in param_range:
                model = compute_model(X, y, param, param_is_k)
                fl.write("{0},\n".format(model))
                fl.flush()
                print model
                yield model

if __name__ == '__main__':
    
#     path = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/mutagenicity/"
    path = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/6_Results/svm/nci_hiv/"
#     path = "/home/stud/ivanovi/Thesis/svm/nci_hiv/"
     
#     wl_props = helpers.svm_light_format_datasets["mutagenicity"]
#     wl_props = helpers.svm_light_format_datasets["nci-hiv"]["A-vs-M"]
#     wl_props = helpers.svm_light_format_datasets["nci-hiv"]["AM-vs-I"]
    wl_props = helpers.svm_light_format_datasets["nci-hiv"]["A-vs-I"]
     
#     output_file = path + "radius_pos_neigh_count_mut"
    output_file = path + "radius_pos_neigh_count_A_vs_I"
     
    print "Start"
     
#     # Only for Mutagenicity
#     override_targets = None
#     k_range = None # [1, 5, 10, 15, 25, 50, 75, 100, 125, 150]
#     radius_range = [0.01, 0.1] + [float(x) for x in range(1, 21)]
     
#     # Only for A_vs_M
#     override_targets = np.vectorize(lambda t: 1 if t == 2 else -1)
#     k_range = None # [1, 5, 10, 50, 100, 500, 1000, 1500]
#     radius_range = [0.01, 0.1, 1., 2., 3., 4., 5., 10., 12.5, 15., 17.5, 20., 25., 30., 50.]
 
    # Only for AM_vs_I and A_vs_I
    override_targets = np.vectorize(lambda t: 1 if t == 2 else t)
    k_range = None # [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]
    radius_range = [0.01, 0.1, 1., 2., 3., 4., 5., 10., 12.5, 15., 17.5, 20., 25., 30., 50.]
     
    data_file_templ = path + wl_props["file_template"]
    wl_iter_range = range(0, 12)
     
    models = get_positive_neighbors_models(data_file_templ, output_file, wl_iter_range,
                                       k_range=k_range, radius_range=radius_range, override_tergets_function=override_targets)
    
    print arrange_results(models, False)
     
    print "Done."
