'''
Created on Dec 17, 2015

@author: Ivan Ivanov
'''

from rdflib import Namespace

data_path = "../data/"
data_ext_path = "../data/ext/"
datasets = {
    "dummy": {
        "files": [data_path + "Dummy/dummy.rdf"]
    },
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
    },
    "famont-ext": {
         "files": [
            data_ext_path + "famont_ext.rdf"
        ]
    },
    "tele-ext": {
         "files": [
            data_ext_path + "tele_ext.rdf"
        ]
    },
    "peel-ext": {
         "files": [
            data_ext_path + "peel_ext.rdf"
        ]
    }
}