'''
Created on Dec 29, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_nodes_mining import feature_extraction,\
    fingerprint, shingle_extraction
from ivanov.graph.algorithms.similar_nodes_mining.min_hash_function import MinHashFunction
from ivanov.graph.algorithms.similar_nodes_mining.sketch_matrix import SketchMatrix
from ivanov.graph.algorithms import similar_nodes_mining
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import algorithms
import networkx as nx
import numpy as np
import unittest
from ivanov.graph.algorithms.similar_nodes_mining.characteristic_matrix import CharacteristicMatrix

class TestSimilarNodesMining(unittest.TestCase):
    dummy_graph = nx.MultiDiGraph()
    dummy_graph.add_node(1, labels=["r"])
    dummy_graph.add_node(2, labels=["r"])
    dummy_graph.add_node(3, labels=["r"])
    dummy_graph.add_node(4, labels=["b"])
    dummy_graph.add_node(5, labels=["r"])
    dummy_graph.add_node(6, labels=["b"])
    dummy_graph.add_node(7, labels=["b"])
    dummy_graph.add_node(8, labels=["b", "r"])
    dummy_graph.add_node(9, labels=["r"])
    dummy_graph.add_node(10, labels=["b"])
    dummy_graph.add_node(11, labels=["b", "r"])
    dummy_graph.add_node(12, labels=["b", "r"])
    dummy_graph.add_edge(1, 8, label="g")
    dummy_graph.add_edge(2, 1, label="n")
    dummy_graph.add_edge(2, 3, label="g")
    dummy_graph.add_edge(3, 5, label="n")
    dummy_graph.add_edge(3, 6, label="n")
    dummy_graph.add_edge(4, 3, label="g")
    dummy_graph.add_edge(6, 2, label="n")
    dummy_graph.add_edge(7, 2, label="n")
    dummy_graph.add_edge(8, 7, label="n")
    dummy_graph.add_edge(8, 9, label="n")
    dummy_graph.add_edge(10, 8, label="g")
    dummy_graph.add_edge(11, 1, label="n")
    dummy_graph.add_edge(11, 12, label="n")
    
    dummy_graph_features = []
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_2", labels=["r"])
    dummy_graph_features[-1].add_node("n_1", labels=["r"])
    dummy_graph_features[-1].add_edge("n_2", "n_1", label="n")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_2", labels=["r"])
    dummy_graph_features[-1].add_node("n_3", labels=["r"])
    dummy_graph_features[-1].add_edge("n_2", "n_3", label="g")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_2", labels=["wl_7"])
    dummy_graph_features[-1].add_node("n_1", labels=["wl_6"])
    dummy_graph_features[-1].add_edge("n_2", "n_1", label="wl_4")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_2", labels=["wl_7"])
    dummy_graph_features[-1].add_node("n_3", labels=["wl_5"])
    dummy_graph_features[-1].add_edge("n_2", "n_3", label="wl_3")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_2", labels=["r"])
    dummy_graph_features[-1].add_node("n_6", labels=["b"])
    dummy_graph_features[-1].add_edge("n_6", "n_2", label="n")
    
    dummy_graph_features.append(nx.MultiDiGraph())
    dummy_graph_features[-1].add_node("n_2", labels=["r"])
    dummy_graph_features[-1].add_node("n_7", labels=["b"])
    dummy_graph_features[-1].add_edge("n_7", "n_2", label="n")
    
    dummy_feature = nx.MultiDiGraph()
    dummy_feature.add_node("n_1", labels=["1", "2"])
    dummy_feature.add_node("n_2", labels=["3"])
    dummy_feature.add_node("n_3", labels=["4", "5", "6"])
    dummy_feature.add_edge("n_1", "n_2", label="7")
    dummy_feature.add_edge("n_3", "n_1", label="7")
    
    raw_ch_matrix_exp = {9591196679437604257: set([0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11]), 9591196679437600161: set([0, 5, 6, 7, 8, 9, 10, 11]), 291392442519547772: set([0, 1, 2, 3, 4, 5, 7, 8, 10]), 11943967864708356199: set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]), 12477866579637637325: set([0, 1, 5, 6, 7, 11]), 3187340149550852624: set([0, 2, 5, 6, 7, 8, 9, 10, 11]), 1816259076396273001: set([8, 4, 7]), 2652763168619356858: set([0, 1, 3, 4, 5, 6, 7, 11]), 291392442519551868: set([0, 1, 10, 5, 7])}
    
    ch_matrix_jaccard_sim_exp = np.array([
        [0.,0.75,0.375,0.5,0.44444445,1.,0.75,0.8888889,0.55555558,0.5,0.75,0.75],
        [0.,0.,0.2857143,0.66666669,0.5714286,0.75,0.5,0.66666669,0.33333334,0.25,0.5,0.5],
        [0.,0.,0.,0.40000001,0.33333334,0.375,0.2857143,0.33333334,0.5,0.40000001,0.5,0.2857143],
        [0.,0.,0.,0.,0.80000001,0.5,0.42857143,0.44444445,0.42857143,0.33333334,0.42857143,0.42857143],
        [0.,0.,0.,0.,0.,0.44444445,0.375,0.55555558,0.5714286,0.2857143,0.375,0.375],
        [0.,0.,0.,0.,0.,0.,0.75,0.8888889,0.55555558,0.5,0.75,0.75],
        [0.,0.,0.,0.,0.,0.,0.,0.66666669,0.5,0.66666669,0.5,1.],
        [0.,0.,0.,0.,0.,0.,0.,0.,0.66666669,0.44444445,0.66666669,0.66666669],
        [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.66666669,0.71428573,0.5],
        [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.66666669,0.66666669],
        [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.5],
        [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]], dtype=np.float32)
    
    def testFeatureExtraction(self):
        labels_list_exp = [
            "g", "n", "r",
            "wl_0;in(wl_2),out(wl_2)", "wl_1;in(wl_2),out(wl_2)", "wl_2;in(wl_0)", "wl_2;in(wl_1)", "wl_2;out(wl_0,wl_1)",
            "wl_3;in(wl_7),out(wl_5)", "wl_4;in(wl_7),out(wl_6)", "wl_5;in(wl_3)", "wl_6;in(wl_4)", "wl_7;out(wl_3,wl_4)",
            "b",
            "wl_13;out(wl_1)", "wl_1;in(wl_13),out(wl_2)", "wl_2;in(wl_1,wl_1)"
        ]
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        features, labels_list = feature_extraction.extract_features("n_2", dummy_hypergraph, r_in=1, r_out=1, r_all=0, wl_iterations=4)
        self.assertEqual(labels_list_exp, labels_list, "The wrong labels lists were computed by Weisfeiler-Lehman.")
        isomorphic = all([algorithms.isomorphic(features[i], self.dummy_graph_features[i]) for i in range(len(features))])
        self.assertTrue(isomorphic, "Wrong features extracted.")
    
    def testRabinFingerprint(self):
        dummy_binary_value = int(216904387105353984940539780098)
        fp_exp = np.uint64(9332362780641028011)
        fp = fingerprint.rabin_fingerprint(dummy_binary_value)
        self.assertEqual(fp_exp, fp, "The calculated fingerprint is wrong.")
    
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
        a = int(6638699916324237062) # random number
        b = int(13296106891814937365) # random number
        h = MinHashFunction(a, b)
        
        fp_exp = np.uint64(13099543915633819982)
        fp = fingerprint.get_minhash_fingerprint_naive(self.dummy_feature, h)
        self.assertEqual(fp_exp, fp, "The minhash fingerprint extracted from the feature is not correct.")
    
    def testCharacteristicMatrix(self):
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        ch_matrix = CharacteristicMatrix(dummy_hypergraph, r_in=3, r_out=2, r_all=0, wl_iterations=0)
        self.assertEqual(self.raw_ch_matrix_exp, ch_matrix.sparse_matrix, "The computed characteristic matrix is wrong.")
    
    def testCharacteristicMatrix_ReadWrite(self):
        file_name = "test_files/characteristic_matrix.tmp"
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        ch_matrix = CharacteristicMatrix(dummy_hypergraph, r_in=2, r_out=2, r_all=0, wl_iterations=4)
        ch_matrix.save_to_file(file_name)
        read_ch_matrix = CharacteristicMatrix.load_from_file(file_name)
        self.assertEqual(read_ch_matrix, ch_matrix, "The read characteristic matrix is different from the saved one.")
    
    def testCharacteristicMatrix_JaccardSimMatrix(self):
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        ch_matrix = CharacteristicMatrix(dummy_hypergraph, r_in=3, r_out=2, r_all=0, wl_iterations=0)
        ch_matrix_jaccard_sim = ch_matrix.compute_jaccard_similarity_matrix()
        equality = (self.ch_matrix_jaccard_sim_exp == ch_matrix_jaccard_sim).all()
        self.assertTrue(equality, "The computed Jaccard similarity matrix is wrong.")

    def testSimilarNodesMining(self):
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        ch_matrix = CharacteristicMatrix(dummy_hypergraph, r_in=3, r_out=2, r_all=0, wl_iterations=0)
        ch_matrix_jaccard_sim = ch_matrix.compute_jaccard_similarity_matrix()
        similarity_matrix_exp = np.array(ch_matrix_jaccard_sim >= 0.8, dtype=np.float32)
        sketch_matrix = SketchMatrix(25, 265, ch_matrix)
        similarity_matrix, _ = similar_nodes_mining.get_node_similarity_matrix(sketch_matrix)
        equality = (similarity_matrix_exp == similarity_matrix).all()
        self.assertTrue(equality, "The computed similarity matrix is wrong (Keep in mind that the sketch_matrix is probabilistic, therefore, it may not be always correct. The test may pass in another run.).")
    
    def testSketchMatrix_ReadWrite(self):
        file_name = "test_files/sketch_matrix.tmp"
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        ch_matrix = CharacteristicMatrix(dummy_hypergraph, r_in=2, r_out=2, r_all=0, wl_iterations=4)
        sketch_matrix = SketchMatrix(5, 20, ch_matrix)
        sketch_matrix.save_to_file(file_name)
        read_sketch_matrix = SketchMatrix.load_from_file(file_name)
        equality = (read_sketch_matrix.matrix == sketch_matrix.matrix).all()
        self.assertTrue(equality, "The read sketch matrix is different from the saved one.")
    
    def testGetSimilarNodes(self):
        dummy_sim_matrix_1 = np.array([
            [0., 1., 1., 1.],
            [0., 0., 1., 1.],
            [0., 0., 0., 1.],
            [0., 0., 0., 0.]])
        dummy_sim_matrix_2 = np.array([
            [0., 1., 1., 1.],
            [0., 0., 0., 1.],
            [0., 0., 0., 0.],
            [0., 0., 0., 0.]])
        dummy_sim_matrix_3 = np.array([
            [0., 1., 0., 0.],
            [0., 0., 1., 0.],
            [0., 0., 0., 1.],
            [0., 0., 0., 0.]])
        cols_nodes_map = {0: "a", 1: "b", 2: "c", 3: "d"}
        
        # TODO: is this way of similar nodes extraction good?
        similar_nodes_1_exp = [["a", "b", "c", "d"], ["b", "c", "d"], ["c", "d"]]
        similar_nodes_2_exp = [["a", "b", "c", "d"], ["b", "d"]]
        similar_nodes_3_exp = [["a", "b"], ["b", "c"], ["c", "d"]]
        
        similar_nodes_1 = similar_nodes_mining.get_similar_nodes(dummy_sim_matrix_1, cols_nodes_map)
        similar_nodes_2 = similar_nodes_mining.get_similar_nodes(dummy_sim_matrix_2, cols_nodes_map)
        similar_nodes_3 = similar_nodes_mining.get_similar_nodes(dummy_sim_matrix_3, cols_nodes_map)
        self.assertEqual(similar_nodes_1_exp, similar_nodes_1, "Wrong similar nodes were extracted.")
        self.assertEqual(similar_nodes_2_exp, similar_nodes_2, "Wrong similar nodes were extracted.")
        self.assertEqual(similar_nodes_3_exp, similar_nodes_3, "Wrong similar nodes were extracted.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFeatureExtraction']
    unittest.main()