'''
Created on Dec 17, 2015

@author: Ivan Ivanov
'''

from rdflib import Namespace

data_path = "../data/"
data_ascii_path = "../data/ascii/"
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
    "tele-ascii": {
        "files": [
#             data_ascii_path + "tele/ontology/code.rdf",
#             data_ascii_path + "tele/ontology/genre.n3",
#             data_ascii_path + "tele/ontology/geography.rdf",
#             data_ascii_path + "tele/ontology/geonames_ontology_v3.1.rdf",
#             data_ascii_path + "tele/ontology/measurement.rdf",
#             data_ascii_path + "tele/ontology/metric.rdf",
#             data_ascii_path + "tele/ontology/money.n3",
#             data_ascii_path + "tele/ontology/ogp.n3",
#             data_ascii_path + "tele/ontology/quantity.rdf",
            data_ascii_path + "tele/capitals.rdf",
            data_ascii_path + "tele/continents.rdf",
            data_ascii_path + "tele/countries.rdf",
            data_ascii_path + "tele/currencies.rdf"
        ]
    },
    "peel": {
         "files": [
            data_path + "Peel/peel.rdf"
        ]
    },
    "peel-ascii": {
         "files": [
            data_ascii_path + "peel/peel.rdf"
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