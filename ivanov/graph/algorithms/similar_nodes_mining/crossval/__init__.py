'''
Created on Feb 9, 2016

@author: Ivan Ivanov
'''
from ivanov.graph.algorithms.similar_graphs_mining import crossval as sgm_crossval
from ivanov.graph.algorithms import similar_nodes_mining, similar_graphs_mining


def model(r_in, r_out, r_all):
    return {"r_in": r_in, "r_out": r_out, "r_all": r_all}

def loo_crossval(hypergraph, wl_iter_range, r_in_range, r_out_range, r_all_range, output_dir, k_L_range=None, infl_point_range=None, p_range=None):
    best_model = sgm_crossval.model(-1, -1, base_model=model(-1, -1, -1))
    
    for r_in in r_in_range:
        for r_out in r_out_range:
            for r_all in r_all_range:
                base_model = model(r_in, r_out, r_all)
                rballs_database, _ = similar_nodes_mining.extract_rballs_database(hypergraph, r_in=r_in, r_out=r_out, r_all=r_all, center_default_color=True)
                rballs_database = [(r_id, list(graphs), t) for r_id, graphs, t in rballs_database] # execute generator
                if k_L_range:
                    current_model = sgm_crossval.loo_crossval_sketch(rballs_database, wl_iter_range, k_L_range, output_dir, base_model=base_model)
                elif infl_point_range:
                    current_model = sgm_crossval.loo_crossval_threshold(rballs_database, wl_iter_range, infl_point_range, output_dir, base_model=base_model)
                else:
                    current_model = sgm_crossval.loo_crossval_pnn(rballs_database, wl_iter_range, p_range, output_dir, base_model=base_model)
                if current_model["quality"] > best_model["quality"]:
                    best_model = current_model
    
    models_file = open(output_dir + "models", "a")
    models_file.write(str(best_model) + ",\n")
    models_file.close()
    
    return best_model
