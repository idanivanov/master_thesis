'''
Created on Nov 24, 2015

@author: Ivan Ivanov
'''

from networkx.readwrite import json_graph
import codecs
import json

def save_graph(nx_graph, file_name):
    node_link_data = json_graph.node_link_data(nx_graph)
    fp = codecs.open(file_name, "w", "utf-8")
    json.dump(node_link_data, fp)
    fp.close()

def load_graph(file_name):
    fp = codecs.open(file_name, "r", "utf-8")
    json_data = json.load(fp)
    fp.close()
    nx_graph = json_graph.node_link_graph(json_data)
    return nx_graph