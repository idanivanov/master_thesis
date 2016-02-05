'''
Created on Feb 4, 2016

@author: Ivan Ivanov
'''
from ivanov.graph import dataset_manager
from ivanov import helpers

path = "data/"

if __name__ == '__main__':
    in_file = helpers.datasets["mutagenicity"]["files"][0]
    graph_database, chem_props = dataset_manager.read_chemical_compounts(in_file)
    print chem_props