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
    "homepages": {
        "files": [
            data_path + "Benchmark/homepages-fixed.nt"
        ]
    },
    "geocoordinates": {
        "files": [
            data_path + "Benchmark/geocoordinates-fixed.nt"
        ]
    },
    "drugadmin": {
        "files": [
            data_path + "DrugAdmin/drugadmin.ttl"
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
    },
    "mutagenicity": {
        "files": [
            data_path + "Mutagenicity/mutagenicity.txt"
        ]
    },
    "mutagenicity-rdf": {
        "files": [
            data_path + "Mutagenicity_RDF/mutagenesis.owl"
        ],
        "compounds_targets": {
            "sample-188": data_path + "Mutagenicity_RDF/compounds_targets_sample_188",
            "sample-42": data_path + "Mutagenicity_RDF/compounds_targets_sample_42"
        }
    },
    "carcinogenesis-rdf-owl": {
        "files": [
            data_path + "Carcinogenesis_RDF/carcinogenesis.owl"
        ],
        "compounds_targets": {
            "sample-330": data_path + "Carcinogenesis_RDF/compounds_targets_330",
            "sample-340": data_path + "Carcinogenesis_RDF/compounds_targets_340",
            "sample-298": data_path + "Carcinogenesis_RDF/compounds_targets_298",
            "sample-MUTAG-340": data_path + "Carcinogenesis_RDF/compounds_targets_MUTAG_340",
        },
        "positives-file" : data_path + "Carcinogenesis_RDF/pos.txt",
        "negatives-file" : data_path + "Carcinogenesis_RDF/neg.txt",
    },
    "carcinogenesis-rdf-ttl": {
        "files": [
            data_path + "Carcinogenesis_RDF/carcinogenesis.ttl"
        ],
        "compounds_targets": {
            "sample-330": data_path + "Carcinogenesis_RDF/compounds_targets_330",
            "sample-340": data_path + "Carcinogenesis_RDF/compounds_targets_340",
            "sample-298": data_path + "Carcinogenesis_RDF/compounds_targets_298",
            "sample-MUTAG-340": data_path + "Carcinogenesis_RDF/compounds_targets_MUTAG_340",
        },
        "positives-file" : data_path + "Carcinogenesis_RDF/pos.txt",
        "negatives-file" : data_path + "Carcinogenesis_RDF/neg.txt",
    },
    "nci-hiv": {
        "files": [
            data_path + "NCI_HIV/AIDS99.txt"
        ]
    },
    "nci-hiv-sample": {
        "files": [
            data_path + "NCI_HIV/AIDS99_sample.txt"
        ]
    }
}

'''svm_light_format_datasets Format:
dataset-name: {
    [sub-dataset-name: {]
        examples_count: Number of records in the dataset.
        file_template: Template of the file path where the data is stored.
        dim_wl_iter_i: Dimensionality of the data for Weisfeiler & Lehman iteration i.
    [}]
}
'''
svm_light_format_datasets = {
    "mutagenicity": {
        "examples_count": 188,
        "file_template": "data/mut_data_wl_{0}",
        "dim_wl_iter_0": 57,
        "dim_wl_iter_1": 166,
        "dim_wl_iter_2": 414,
        "dim_wl_iter_3": 766,
        "dim_wl_iter_4": 1305,
        "dim_wl_iter_5": 1970,
        "dim_wl_iter_6": 3000,
        "dim_wl_iter_7": 4212,
        "dim_wl_iter_8": 5781,
        "dim_wl_iter_9": 7499,
        "dim_wl_iter_10": 9475,
        "dim_wl_iter_11": 11522
    },
    "nci-hiv": {
        "A-vs-M": {
            "examples_count": 1503,
            "file_template": "data/A_vs_M/svm_light_data_wl_{0}",
            "dim_wl_iter_0": 3197528,
            "dim_wl_iter_1": 3197921,
            "dim_wl_iter_2": 3197992,
            "dim_wl_iter_3": 3197994,
            "dim_wl_iter_4": 3197997,
            "dim_wl_iter_5": 3198002,
            "dim_wl_iter_6": 3198007,
            "dim_wl_iter_7": 3198014,
            "dim_wl_iter_8": 3198021,
            "dim_wl_iter_9": 3198030,
            "dim_wl_iter_10": 3198039,
            "dim_wl_iter_11": 3198049
        },
        "AM-vs-I": {
            "examples_count": 42687,
            "file_template": "data/AM_vs_I/svm_light_data_wl_{0}",
            "dim_wl_iter_0": 3198276,
            "dim_wl_iter_1": 3198277,
            "dim_wl_iter_2": 3198961,
            "dim_wl_iter_3": 3200095,
            "dim_wl_iter_4": 3200100,
            "dim_wl_iter_5": 3200105,
            "dim_wl_iter_6": 3200112,
            "dim_wl_iter_7": 3200120,
            "dim_wl_iter_8": 3200132,
            "dim_wl_iter_9": 3200145,
            "dim_wl_iter_10": 3200163,
            "dim_wl_iter_11": 3200181
        },
        "A-vs-I": {
            "examples_count": 41606,
            "file_template": "data/A_vs_I/svm_light_data_wl_{0}",
            "dim_wl_iter_0": 3198276,
            "dim_wl_iter_1": 3198277,
            "dim_wl_iter_2": 3198961,
            "dim_wl_iter_3": 3200095,
            "dim_wl_iter_4": 3200100,
            "dim_wl_iter_5": 3200105,
            "dim_wl_iter_6": 3200112,
            "dim_wl_iter_7": 3200120,
            "dim_wl_iter_8": 3200132,
            "dim_wl_iter_9": 3200145,
            "dim_wl_iter_10": 3200163,
            "dim_wl_iter_11": 3200181
        }
    }
}