'''
Created on Dec 29, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_nodes_mining import feature_extraction,\
    fingerprint, shingle_extraction
from ivanov.graph.algorithms.similar_nodes_mining.sketch_matrix import SketchMatrix
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import algorithms
import networkx as nx
import numpy as np
import unittest


class TestSimilarNodesMining(unittest.TestCase):
    
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
    
    dummy_graph_features = []
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_7", labels=["7"])
    dummy_graph_features[-1].add_node("n_8", labels=["8"])
    dummy_graph_features[-1].add_edge("n_7", "n_8", label="0")
    
#     dummy_graph_features.append(nx.MultiDiGraph())
#     dummy_graph_features[-1].add_node("n_7", labels=["1"])
#     dummy_graph_features[-1].add_node("n_8", labels=["2"])
#     dummy_graph_features[-1].add_edge("n_7", "n_8", label="0")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_7", labels=["7"])
    dummy_graph_features[-1].add_node("n_4", labels=["4"])
    dummy_graph_features[-1].add_edge("n_4", "n_7", label="0")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_7", labels=["7"])
    dummy_graph_features[-1].add_node("n_5", labels=["5"])
    dummy_graph_features[-1].add_edge("n_5", "n_7", label="0")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_7", labels=["7"])
    dummy_graph_features[-1].add_node("n_1", labels=["1"])
    dummy_graph_features[-1].add_edge("n_1", "n_7", label="0")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_7", labels=["wl_12"])
    dummy_graph_features[-1].add_node("n_4", labels=["wl_14"])
    dummy_graph_features[-1].add_edge("n_4", "n_7", label="wl_10")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_7", labels=["wl_12"])
    dummy_graph_features[-1].add_node("n_5", labels=["wl_15"])
    dummy_graph_features[-1].add_edge("n_5", "n_7", label="wl_11")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_7", labels=["wl_12"])
    dummy_graph_features[-1].add_node("n_1", labels=["wl_13"])
    dummy_graph_features[-1].add_edge("n_1", "n_7", label="wl_9")
    
    dummy_feature = nx.MultiDiGraph()
    dummy_feature.add_node("n_1", labels=["1", "2"])
    dummy_feature.add_node("n_2", labels=["3"])
    dummy_feature.add_node("n_3", labels=["4", "5", "6"])
    dummy_feature.add_edge("n_1", "n_2", label="7")
    dummy_feature.add_edge("n_3", "n_1", label="7")
    
    def testFeatureExtraction(self):
        labels_lists_exp = [
            '0', '7', '8',
            'wl_0;wl_1,wl_2', 'wl_1;wl_0', 'wl_2;wl_0',
            '1', '4', '5',
            'wl_0;wl_1,wl_6', 'wl_0;wl_1,wl_7', 'wl_0;wl_1,wl_8', 'wl_1;wl_0,wl_0,wl_0', 'wl_6;wl_0', 'wl_7;wl_0', 'wl_8;wl_0',
            'wl_10;wl_12,wl_14', 'wl_11;wl_12,wl_15', 'wl_12;wl_10,wl_11,wl_9', 'wl_13;wl_9', 'wl_14;wl_10', 'wl_15;wl_11', 'wl_9;wl_12,wl_13'
        ]
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        features, labels_lists = feature_extraction.extract_features("n_7", dummy_hypergraph, r_in=1, r_out=1, r_all=0, wl_iterations=4)
        self.assertEqual(labels_lists_exp, labels_lists, "The wrong labels lists were computed by Weisfeiler-Lehman.")
        isomorphic = all([algorithms.isomorphic(features[i], self.dummy_graph_features[i]) for i in range(len(features))])
        self.assertTrue(isomorphic, "Wrong features extracted.")
    
    def testRabinFingerprint(self):
        dummy_binary_array = np.array([1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0])
        fp = fingerprint.rabin_fingerprint(dummy_binary_array)
        self.assertEqual(9332362780641026048, fp, "The calculated fingerprint is wrong.")
    
    def testShingleExtraction(self):
        shingles_exp = [
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((1,0))),4),1)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((1,0))),5),1)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((1,0))),6),1)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((1,0))),4),2)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((1,0))),5),2)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((1,0))),6),2)"
        ]
        shingles = shingle_extraction.extract_shingles(self.dummy_feature)
        self.assertEqual(shingles_exp, list(shingles), "Wrong shingles were extracted from feature.")
    
    def testGetMinhashFingerprintNaive(self):
        a = 6638699916324237062 # random number
        b = 13296106891814937365 # random number
        prime = 18446744073709551629 # the first prime after 2^64
        r = 18446744073709551616 # 2^64
        h = lambda x: (int(int(a * x) + b) % prime) % r
        
        fp_exp = 13099543911338852352
        fp = fingerprint.get_minhash_fingerprint_naive(self.dummy_feature, h)
        self.assertEqual(fp_exp, fp, "The minhash fingerprint extracted from the feature is not correct.")

#     def testSketchMatrix(self):
#         dummy_hypergraph = Hypergraph(self.dummy_graph)
#         sketch = SketchMatrix(10, 10, dummy_hypergraph, r_in=1, r_out=1, r_all=0, wl_iterations=4)
#         print sketch

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFeatureExtraction']
    unittest.main()