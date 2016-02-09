'''
Created on Feb 9, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms import similar_nodes_mining, similar_graphs_mining
from ivanov.graph.algorithms.similar_graphs_mining import crossval as sgm_crossval


def model_threshold(quality, wl_iterations, r_in, r_out, r_all, k=-1, L=-1, infl_point=-1):
    m = sgm_crossval.model_threshold(quality, wl_iterations, k, L, infl_point)
    return model(m, r_in, r_out, r_all)

def model_p(quality, wl_iterations, r_in, r_out, r_all, p):
    m = sgm_crossval.model_p(quality, wl_iterations, p)
    return model(m, r_in, r_out, r_all)

def model(pre_model, r_in, r_out, r_all):
    m = pre_model.copy()
    m.update({"r_in": r_in, "r_out": r_out, "r_all": r_all})
    return m

def loo_crossval_sketch(hypergraph, wl_iter_range, k_L_range, r_in_range, r_out_range, r_all_range, output_dir):
    best_model = model_threshold(-1, -1, -1, -1, -1)
    
    for r_in in r_in_range:
        for r_out in r_out_range:
            for r_all in r_all_range:
                rballs_database, _ = similar_nodes_mining.extract_rballs_database(hypergraph, r_in=r_in, r_out=r_out, r_all=r_all)
                cols_count = hypergraph.number_of_nodes()
                target_values = map(lambda n: hypergraph.node[n]["labels"], hypergraph.nodes_iter())
                pre_model = sgm_crossval.loo_crossval_sketch(rballs_database, cols_count, target_values, wl_iter_range, k_L_range, output_dir)
                if pre_model["quality"] > best_model["quality"]:
                    best_model = model(pre_model, r_in, r_out, r_all)
    
    return best_model

def loo_crossval_pnn(hypergraph, wl_iter_range, p_range, r_in_range, r_out_range, r_all_range, output_dir):
    best_model = model_p(-1, -1, -1, -1, -1, -1)
    
    for r_in in r_in_range:
        for r_out in r_out_range:
            for r_all in r_all_range:
                rballs_database, _ = similar_nodes_mining.extract_rballs_database(hypergraph, r_in=r_in, r_out=r_out, r_all=r_all)
                cols_count = hypergraph.number_of_nodes()
                target_values = map(lambda n: hypergraph.node[n]["labels"], hypergraph.nodes_iter())
                pre_model = sgm_crossval.loo_crossval_pnn(rballs_database, cols_count, target_values, wl_iter_range, p_range, output_dir)
                print model(pre_model, r_in, r_out, r_all)
                if pre_model["quality"] > best_model["quality"]:
                    best_model = model(pre_model, r_in, r_out, r_all)
    
    return best_model
