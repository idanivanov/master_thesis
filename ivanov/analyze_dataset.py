'''
Created on Dec 8, 2015

@author: Ivan Ivanov
'''

from ivanov.graph import rdf
from rdflib import Namespace
import time
import codecs

data_path = "../data/"
datasets = {
    "famont" : {
        "files": [data_path + "family.rdf.owl.rdf"]
    },
    "tele": {
        "files": [
            data_path + "Telegraphis/ontology/code.rdf",
            data_path + "Telegraphis/ontology/genre.n3",
            data_path + "Telegraphis/ontology/geography.rdf",
            data_path + "Telegraphis/ontology/geonames_ontology_v3.1.rdf",
            data_path + "Telegraphis/ontology/measurement.rdf",
            data_path + "Telegraphis/ontology/metric.rdf",
            data_path + "Telegraphis/ontology/money.n3",
            data_path + "Telegraphis/ontology/ogp.n3",
            data_path + "Telegraphis/ontology/quantity.rdf",
            data_path + "Telegraphis/capitals.rdf",
            data_path + "Telegraphis/continents.rdf",
            data_path + "Telegraphis/countries.rdf",
            data_path + "Telegraphis/currencies.rdf"
        ]
    },
    "peel": {
         "files": [
            data_path + "Peel/peel.rdf"
        ]
    },
    "lexvo": {
        "ns": Namespace(u"http://lexvo.org/ontology#"),
        "files": [
            data_path + "Lexvo/ontology.xsl",
            data_path + "Lexvo/lexvo_2013-02-09.rdf"
        ]
    },
    "geospecies": {
         "files": [
            data_path + "GeoSpecies/geospecies.rdf"
        ]
    },
    "jamendo": {
         "files": [
            data_path + "Jamendo/jamendo-rdf/jamendo.rdf",
            data_path + "Jamendo/jamendo-rdf/mbz_jamendo.rdf"
        ]
    },
    "opencyc": {
         "files": [
            data_path + "OpenCyc/opencyc-latest.owl"
        ]
    }
}

def extract_nodes(dataset_id):
    dataset = datasets[dataset_id]
    
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
    
    dataset = datasets[dataset_id]
    
    start = time.time()
    rdf_graph = rdf.read_graph(dataset["files"])
    end = time.time()
    print ("Reading graph took: {0} s.").format(end - start)
    
    print "Blank nodes:", len(set(rdf.get_blank_nodes(rdf_graph)))