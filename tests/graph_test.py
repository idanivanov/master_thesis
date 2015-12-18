'''
Created on Dec 18, 2015

@author: Ivan Ivanov
'''

import networkx as nx
import unittest
from ivanov.graph.hypergraph import Hypergraph

class GraphTest(unittest.TestCase):
    dummy_graph = nx.MultiDiGraph()
    dummy_graph.add_node(1, labels = ["1"])
    dummy_graph.add_node(2, labels = ["2"])
    dummy_graph.add_node(3, labels = ["3"])
    dummy_graph.add_node(4, labels = ["4"])
    dummy_graph.add_node(5, labels = ["5"])
    dummy_graph.add_node(6, labels = ["6"])
    dummy_graph.add_node(7, labels = ["7"])
    dummy_graph.add_node(8, labels = ["8"])
    dummy_graph.add_node(9, labels = ["9"])
    dummy_graph.add_node(10, labels = ["10"])
    dummy_graph.add_node(11, labels = ["11"])
    dummy_graph.add_node(12, labels = ["12"])
    dummy_graph.add_node(13, labels = ["13"])
    dummy_graph.add_node(14, labels = ["14"])
    dummy_graph.add_node(15, labels = ["15"])
    dummy_graph.add_node(16, labels = ["16"])
    dummy_graph.add_edge(1, 2, label = "0")
    dummy_graph.add_edge(1, 3, label = "0")
    dummy_graph.add_edge(1, 5, label = "0")
    dummy_graph.add_edge(1, 6, label = "0")
    dummy_graph.add_edge(1, 7, label = "0")
    dummy_graph.add_edge(1, 9, label = "0")
    dummy_graph.add_edge(1, 14, label = "0")
    dummy_graph.add_edge(1, 15, label = "0")
    dummy_graph.add_edge(1, 16, label = "0")
    dummy_graph.add_edge(2, 12, label = "0")
    dummy_graph.add_edge(2, 13, label = "0")
    dummy_graph.add_edge(3, 4, label = "0")
    dummy_graph.add_edge(3, 10, label = "0")
    dummy_graph.add_edge(3, 11, label = "0")
    dummy_graph.add_edge(3, 12, label = "0")
    dummy_graph.add_edge(4, 7, label = "0")
    dummy_graph.add_edge(4, 8, label = "0")
    dummy_graph.add_edge(5, 6, label = "0")
    dummy_graph.add_edge(5, 7, label = "0")
    dummy_graph.add_edge(5, 9, label = "0")
    dummy_graph.add_edge(5, 16, label = "0")
    dummy_graph.add_edge(6, 10, label = "0")
    dummy_graph.add_edge(6, 16, label = "0")
    dummy_graph.add_edge(7, 8, label = "0")
    dummy_graph.add_edge(8, 9, label = "0")
    dummy_graph.add_edge(10, 11, label = "0")
    dummy_graph.add_edge(11, 12, label = "0")
    dummy_graph.add_edge(11, 13, label = "0")
    dummy_graph.add_edge(12, 14, label = "0")
    dummy_graph.add_edge(12, 15, label = "0")
    dummy_graph.add_edge(13, 14, label = "0")
    dummy_graph.add_edge(13, 15, label = "0")
    
    def testHypergraph_Copy(self):
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        dummy_copy = dummy_hypergraph.copy()
        self.assertEqual(dummy_hypergraph, dummy_copy, "The copy was not correct.")

    def testHypergraph_ReadWrite(self):
        file_name = "test_files/dummy_hypergraph"
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        dummy_hypergraph.save_to_file(file_name)
        read_hypergraph = Hypergraph.load_from_file(file_name)
        self.assertEqual(dummy_hypergraph, read_hypergraph, "The read hypergraph is different from the saved one.")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testHypergraphReadWrite']
    unittest.main()