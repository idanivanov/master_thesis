'''
Created on Jun 22, 2016

@author: ivan
'''
from ivanov import helpers
from ivanov.graph import dataset_manager
import time

if __name__ == '__main__':
    with open("runtime", "w") as out_fl:
        dataset = "carcinogenesis-rdf-owl"
        in_files = helpers.datasets[dataset]["files"]
        compounds_targets_file = helpers.datasets[dataset]["compounds_targets"]["sample-340"]
        uri_prefix = "http://dl-learner.org/carcinogenesis#"
        output_dir = "/media/ivan/204C66C84C669874/Uni-Bonn/Thesis/Main/5_Complete_Project/Workspace/master_thesis/output_chem/carcinogenesis_rdf/runtime_340/data_w_{0}/"
        for w in range(1, 21):
            for wl_iter in range(6):
                start = time.time()
                dataset_manager.build_svmlight_chemical_data(in_files, wl_iter, output_dir.format(w), format_rdf=True,
                                                             compounds_targets_file=compounds_targets_file, uri_prefix=uri_prefix,
                                                             shingles_type="w-shingles", window_size=w, accumulate_wl_shingles=True,
                                                             save_just_last_wl_it=True)
                time_elapsed = time.time() - start
                out_fl.write("w={0}, wl_iter={1}, time={2}".format(w, wl_iter, time_elapsed))
                out_fl.flush()