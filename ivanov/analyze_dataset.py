'''
Created on Dec 8, 2015

@author: Ivan Ivanov
'''

from ivanov.graph import rdf
from ivanov import helpers
import time
import codecs

def extract_nodes(dataset_id):
    dataset = helpers.datasets[dataset_id]
    
    start = time.time()
    rdf_graph = rdf.read_graph(dataset["files"])
    end = time.time()
    print ("Reading graph took: {0} s.").format(end - start)
    
    rdf.extract_subjects_by_types(rdf_graph, "../output/stats/{0}/".format(dataset_id))

def compute_stats(dataset_id, files_range):
    def read_class_and_nodes_from_file(file_path):
        fp = codecs.open(file_path, "r", "utf-8")
        class_type = fp.readline()[:-1]
        nodes = set(fp.readlines())
        fp.close()
        return str(class_type), nodes
    
    in_files_dir = "../output/stats/{0}/".format(dataset_id)
    stats = {}
    
    for i in files_range:
        i_str = str(i)
        stats[i_str] = {}
        stats[i_str]["class"], nodes = read_class_and_nodes_from_file(in_files_dir + str(i_str))
        stats[i_str]["len"] = len(nodes)
    
    total = sum(map(lambda x: stats[x]["len"], stats))
    
    stats["all"] = {}
    stats["all"]["len"] = total
    
    return stats
        

if __name__ == '__main__':
#     print compute_stats("jamendo", range(10))
    
    dataset_id = "opencyc"
    
    dataset = helpers.datasets[dataset_id]
    
    start = time.time()
    rdf_graph = rdf.read_graph(dataset["files"])
    end = time.time()
    print ("Reading graph took: {0} s.").format(end - start)
    
    print "Blank nodes:", len(set(rdf.get_blank_nodes(rdf_graph)))