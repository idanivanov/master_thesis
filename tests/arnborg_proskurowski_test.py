'''
Created on Dec 28, 2015

@author: ivan
'''

from ivanov.graph.algorithms import arnborg_proskurowski
import networkx as nx
import unittest
from ivanov.graph.algorithms.arnborg_proskurowski.reducible_feature import ReducibleFeature

class Test(unittest.TestCase):

    # Arnborg & Proskurowski example graph with tree-width 2
    graph_tw_2 = nx.MultiDiGraph()
    graph_tw_2.add_node(1, labels = ["(0)"])
    graph_tw_2.add_node(2, labels = ["(0)"])
    graph_tw_2.add_node(3, labels = ["(0)"])
    graph_tw_2.add_node(4, labels = ["(0)"])
    graph_tw_2.add_node(5, labels = ["(0)"])
    graph_tw_2.add_node(6, labels = ["(0)"])
    graph_tw_2.add_node(7, labels = ["(0)"])
    graph_tw_2.add_node(8, labels = ["(0)"])
    graph_tw_2.add_node(9, labels = ["(0)"])
    graph_tw_2.add_node(10, labels = ["(0)"])
    graph_tw_2.add_node(11, labels = ["(0)"])
    graph_tw_2.add_node(12, labels = ["(0)"])
    graph_tw_2.add_node(13, labels = ["(0)"])
    graph_tw_2.add_node(14, labels = ["(0)"])
    graph_tw_2.add_node(15, labels = ["(0)"])
    graph_tw_2.add_edge(1, 13, label = "0")
    graph_tw_2.add_edge(2, 13, label = "0")
    graph_tw_2.add_edge(2, 14, label = "0")
    graph_tw_2.add_edge(3, 14, label = "0")
    graph_tw_2.add_edge(4, 15, label = "0")
    graph_tw_2.add_edge(5, 6, label = "0")
    graph_tw_2.add_edge(5, 15, label = "0")
    graph_tw_2.add_edge(6, 5, label = "0")
    graph_tw_2.add_edge(6, 7, label = "0")
    graph_tw_2.add_edge(7, 6, label = "0")
    graph_tw_2.add_edge(7, 15, label = "0")
    graph_tw_2.add_edge(8, 12, label = "0")
    graph_tw_2.add_edge(9, 10, label = "0")
    graph_tw_2.add_edge(9, 12, label = "0")
    graph_tw_2.add_edge(10, 9, label = "0")
    graph_tw_2.add_edge(10, 11, label = "0")
    graph_tw_2.add_edge(11, 10, label = "0")
    graph_tw_2.add_edge(11, 12, label = "0")
    graph_tw_2.add_edge(12, 8, label = "0")
    graph_tw_2.add_edge(12, 9, label = "0")
    graph_tw_2.add_edge(12, 11, label = "0")
    graph_tw_2.add_edge(12, 13, label = "0")
    graph_tw_2.add_edge(12, 15, label = "0")
    graph_tw_2.add_edge(13, 1, label = "0")
    graph_tw_2.add_edge(13, 2, label = "0")
    graph_tw_2.add_edge(13, 12, label = "0")
    graph_tw_2.add_edge(13, 14, label = "0")
    graph_tw_2.add_edge(13, 15, label = "0")
    graph_tw_2.add_edge(14, 2, label = "0")
    graph_tw_2.add_edge(14, 3, label = "0")
    graph_tw_2.add_edge(14, 13, label = "0")
    graph_tw_2.add_edge(14, 15, label = "0")
    graph_tw_2.add_edge(15, 4, label = "0")
    graph_tw_2.add_edge(15, 5, label = "0")
    graph_tw_2.add_edge(15, 7, label = "0")
    graph_tw_2.add_edge(15, 12, label = "0")
    graph_tw_2.add_edge(15, 13, label = "0")
    graph_tw_2.add_edge(15, 14, label = "0")

    def testTW_2(self):
        features_expected =[
            ReducibleFeature(1, 2, ["n_4"], ["n_15"]),
            ReducibleFeature(1, 2, ["n_8"], ["n_12"]),
            ReducibleFeature(1, 2, ["n_1"], ["n_13"]),
            ReducibleFeature(1, 2, ["n_3"], ["n_14"]),
            ReducibleFeature(2, 1, ["n_9", "n_10", "n_11"], ["n_12", "n_12"]),
            ReducibleFeature(2, 1, ["n_5", "n_6", "n_7"], ["n_15", "n_15"]),
            ReducibleFeature(2, 1, ["n_2"], ["n_14", "n_13"]),
            ReducibleFeature(2, 1, ["n_14"], ["n_15", "n_13"]),
            ReducibleFeature(2, 1, ["n_12"], ["n_15", "n_13"]),
            ReducibleFeature(1, 1, ["n_15"], ["n_13"])
        ]
        canonical_str_expected = "(1.1;(0.1;(0),(1.2;(0,((0,1),(1,0))),(0))),((0.2;((2.1;((0.2;((2.1;(0,((0,1),(1,0))),(0),(0,((0,1),(1,0)))),((0,1),(1,0))),(0,((0,1),(1,0)))),((0,1),(1,0))),(0.1;(0),(1.2;(0,((0,1),(1,0))),(0))),(0,((0,1),(1,0)))),((0,1))),((2.1;(0,((0,1),(1,0))),(0.1;(0.1;(0),(1.2;(0,((0,1),(1,0))),(0))),(2.1;(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))))),(0,((0,1),(1,0)))),((0,1),(1,0))),(0,((0,1),(1,0)))),((0,1))),(0.1;(0.1;(0),(1.2;(0,((0,1),(1,0))),(0))),(2.1;(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))))))"
        tw, canonical_str, features = arnborg_proskurowski.get_canonical_representation(self.graph_tw_2, return_features=True)
        self.assertEqual(tw, 2, "The tree-width was not estimated correctly.")
        self.assertEqual(canonical_str, canonical_str_expected, "The canonical string was not extracted correctly.")
        self.assertEqual(features, features_expected, "The features were not extracted correctly.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()