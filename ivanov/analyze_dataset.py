'''
Created on Dec 8, 2015

@author: Ivan Ivanov
'''

from ivanov.graph import rdf
import time

data_path = "../data/"
datasets = {
    "famont" : [data_path + "family.rdf.owl.rdf"],
    "lexvo": [
        data_path + "Lexvo/ontology.xsl",
        data_path + "Lexvo/lexvo_2013-02-09.rdf"
    ],
    "tele": [
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
}

if __name__ == '__main__':
    start = time.time()
    rdf_graph = rdf.read_graph(datasets["tele"])
    end = time.time()
    print "Reading graph took: {0} s.".format(end - start)
    
#     rdf.stats(rdf_graph)
    