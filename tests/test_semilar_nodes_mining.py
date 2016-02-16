'''
Created on Dec 29, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_graphs_mining import feature_extraction,\
    fingerprint, shingle_extraction
from ivanov.graph.algorithms import arnborg_proskurowski, similar_nodes_mining,\
    r_ball_hyper
from ivanov.graph.algorithms.similar_graphs_mining.characteristic_matrix import CharacteristicMatrix
from ivanov.graph.algorithms.similar_graphs_mining.min_hash_function import MinHashFunction
from ivanov.graph.algorithms.similar_graphs_mining.sketch_matrix import SketchMatrix
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import algorithms
from tests import example_graphs
import numpy as np
import unittest

class TestSimilarNodesMining(unittest.TestCase):
    
    raw_ch_matrix_exp = {9591196679437604257: set([0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11]), 9591196679437600161: set([0, 5, 6, 7, 8, 9, 10, 11]), 291392442519547772: set([0, 1, 2, 3, 4, 5, 7, 8, 10]), 11943967864708356199: set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]), 12477866579637637325: set([0, 1, 5, 6, 7, 11]), 3187340149550852624: set([0, 2, 5, 6, 7, 8, 9, 10, 11]), 1816259076396273001: set([8, 4, 7]), 2652763168619356858: set([0, 1, 3, 4, 5, 6, 7, 11]), 291392442519551868: set([0, 1, 10, 5, 7])}
    
    ch_matrix_jaccard_sim_exp = np.array([
        [0.0, 0.75, 0.375, 0.5, 0.4444444477558136, 1.0, 0.75, 0.8888888955116272, 0.5555555820465088, 0.5, 0.75, 0.75],
        [0.75, 0.0, 0.2857142984867096, 0.6666666865348816, 0.5714285969734192, 0.75, 0.5, 0.6666666865348816, 0.3333333432674408, 0.25, 0.5, 0.5],
        [0.375, 0.2857142984867096, 0.0, 0.4000000059604645, 0.3333333432674408, 0.375, 0.2857142984867096, 0.3333333432674408, 0.5, 0.4000000059604645, 0.5, 0.2857142984867096],
        [0.5, 0.6666666865348816, 0.4000000059604645, 0.0, 0.800000011920929, 0.5, 0.4285714328289032, 0.4444444477558136, 0.4285714328289032, 0.3333333432674408, 0.4285714328289032, 0.4285714328289032],
        [0.4444444477558136, 0.5714285969734192, 0.3333333432674408, 0.800000011920929, 0.0, 0.4444444477558136, 0.375, 0.5555555820465088, 0.5714285969734192, 0.2857142984867096, 0.375, 0.375],
        [1.0, 0.75, 0.375, 0.5, 0.4444444477558136, 0.0, 0.75, 0.8888888955116272, 0.5555555820465088, 0.5, 0.75, 0.75],
        [0.75, 0.5, 0.2857142984867096, 0.4285714328289032, 0.375, 0.75, 0.0, 0.6666666865348816, 0.5, 0.6666666865348816, 0.5, 1.0],
        [0.8888888955116272, 0.6666666865348816, 0.3333333432674408, 0.4444444477558136, 0.5555555820465088, 0.8888888955116272, 0.6666666865348816, 0.0, 0.6666666865348816, 0.4444444477558136, 0.6666666865348816, 0.6666666865348816],
        [0.5555555820465088, 0.3333333432674408, 0.5, 0.4285714328289032, 0.5714285969734192, 0.5555555820465088, 0.5, 0.6666666865348816, 0.0, 0.6666666865348816, 0.7142857313156128, 0.5],
        [0.5, 0.25, 0.4000000059604645, 0.3333333432674408, 0.2857142984867096, 0.5, 0.6666666865348816, 0.4444444477558136, 0.6666666865348816, 0.0, 0.6666666865348816, 0.6666666865348816],
        [0.75, 0.5, 0.5, 0.4285714328289032, 0.375, 0.75, 0.5, 0.6666666865348816, 0.7142857313156128, 0.6666666865348816, 0.0, 0.5],
        [0.75, 0.5, 0.2857142984867096, 0.4285714328289032, 0.375, 0.75, 1.0, 0.6666666865348816, 0.5, 0.6666666865348816, 0.5, 0.0]], dtype=np.float32)
    
    def testFeatureExtraction(self):
        wl_state_exp = {
            "labels": {
                "g": "wl_0.0",
                "n": "wl_0.1",
                "r": "wl_0.2",
                "b": "wl_0.3",
                "wl_0.0;in(wl_0.2),out(wl_0.2)": "wl_1.0",
                "wl_0.1;in(wl_0.2),out(wl_0.2)": "wl_1.1",
                "wl_0.2;in(wl_0.1)": "wl_1.2",
                "wl_0.2;out(wl_0.0,wl_0.1)": "wl_1.3",
                "wl_0.2;in(wl_0.0)": "wl_1.4",
                "wl_0.1;in(wl_0.3),out(wl_0.2)": "wl_1.5",
                "wl_0.3;out(wl_0.1)": "wl_1.6",
                "wl_0.2;in(wl_0.1,wl_0.1)": "wl_1.7"
            },
            "next_labels": {
                0: 4,
                1: 8
            }
        }
        dummy_hypergraph = Hypergraph(example_graphs.snm_dummy_graph)
        rballs_database = [r_ball_hyper(dummy_hypergraph, "n_2", 1, edge_dir=1),
                           r_ball_hyper(dummy_hypergraph, "n_2", 1, edge_dir=-1)]
        features = []
        wl_state = None
        for rball in rballs_database:
            new_features, wl_state = feature_extraction.extract_features(rball, wl_iterations=1, wl_state=wl_state)
            features += new_features
        self.assertEqual(wl_state_exp, wl_state, "The wrong wl_state was computed by Weisfeiler-Lehman.")
        isomorphic = all([algorithms.isomorphic(features[i], example_graphs.snm_dummy_graph_features[i]) for i in range(len(features))])
        self.assertTrue(isomorphic, "Wrong features extracted.")
    
    def testFeatureTypes(self):
        dummy_hypergraph_2 = Hypergraph(example_graphs.snm_dummy_graph_2)
        features = []
        raw_features = arnborg_proskurowski.get_reduced_features(dummy_hypergraph_2)
        for raw_feature in raw_features:
            new_features = list(feature_extraction.process_raw_feature(raw_feature, dummy_hypergraph_2))
            features += new_features
        isomorphic = all([algorithms.isomorphic(features[i], example_graphs.snm_dummy_graph_features_2[i]) for i in range(len(features))])
        self.assertTrue(isomorphic, "Wrong features extracted.")
    
    def testRabinFingerprint(self):
        dummy_binary_value = int(216904387105353984940539780098)
        fp_exp = np.uint64(9332362780641028011)
        fp = fingerprint.rabin_fingerprint(dummy_binary_value)
        self.assertEqual(fp_exp, fp, "The calculated fingerprint is wrong.")
    
    def testShingleExtraction(self):
        shingles_exp = [
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((0,1),(1,0))),4),1)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(8,((1,0))),4),1)",
            "(0.1;(1.2;(7,((0,1),(1,0))),4),(1.2;(8,((0,1))),3),1)",
            "(0.1;(1.2;(8,((0,1))),3),(1.2;(8,((1,0))),4),1)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((0,1),(1,0))),5),1)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(8,((1,0))),5),1)",
            "(0.1;(1.2;(7,((0,1),(1,0))),5),(1.2;(8,((0,1))),3),1)",
            "(0.1;(1.2;(8,((0,1))),3),(1.2;(8,((1,0))),5),1)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((0,1),(1,0))),6),1)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(8,((1,0))),6),1)",
            "(0.1;(1.2;(7,((0,1),(1,0))),6),(1.2;(8,((0,1))),3),1)",
            "(0.1;(1.2;(8,((0,1))),3),(1.2;(8,((1,0))),6),1)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((0,1),(1,0))),4),2)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(8,((1,0))),4),2)",
            "(0.1;(1.2;(7,((0,1),(1,0))),4),(1.2;(8,((0,1))),3),2)",
            "(0.1;(1.2;(8,((0,1))),3),(1.2;(8,((1,0))),4),2)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((0,1),(1,0))),5),2)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(8,((1,0))),5),2)",
            "(0.1;(1.2;(7,((0,1),(1,0))),5),(1.2;(8,((0,1))),3),2)",
            "(0.1;(1.2;(8,((0,1))),3),(1.2;(8,((1,0))),5),2)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(7,((0,1),(1,0))),6),2)",
            "(0.1;(1.2;(7,((0,1))),3),(1.2;(8,((1,0))),6),2)",
            "(0.1;(1.2;(7,((0,1),(1,0))),6),(1.2;(8,((0,1))),3),2)",
            "(0.1;(1.2;(8,((0,1))),3),(1.2;(8,((1,0))),6),2)"
        ]
        shingles = shingle_extraction.extract_shingles(example_graphs.snm_dummy_feature)
        self.assertEqual(shingles_exp, list(shingles), "Wrong shingles were extracted from feature.")
    
    def testGetMinhashFingerprintNaive(self):
        a = int(6638699916324237062) # random number
        b = int(13296106891814937365) # random number
        h = MinHashFunction(a, b)
        
        fp_exp = np.uint64(17061342891450049721)
        fp = fingerprint.get_minhash_fingerprint_naive(example_graphs.snm_dummy_feature, h)
        self.assertEqual(fp_exp, fp, "The minhash fingerprint extracted from the feature is not correct.")
    
    def testCharacteristicMatrix(self):
        dummy_hypergraph = Hypergraph(example_graphs.snm_dummy_graph)
        rballs_database, _ = similar_nodes_mining.extract_rballs_database(dummy_hypergraph, r_in=3, r_out=2, r_all=0)
        nodes_count = dummy_hypergraph.number_of_nodes()
        ch_matrix = CharacteristicMatrix(rballs_database, nodes_count, wl_iterations=0)
        self.assertEqual(self.raw_ch_matrix_exp, ch_matrix.sparse_matrix, "The computed characteristic matrix is wrong.")
    
    def testCharacteristicMatrix_ReadWrite(self):
        file_name = "test_files/characteristic_matrix.tmp"
        dummy_hypergraph = Hypergraph(example_graphs.snm_dummy_graph)
        rballs_database, _ = similar_nodes_mining.extract_rballs_database(dummy_hypergraph, r_in=2, r_out=2, r_all=0)
        nodes_count = dummy_hypergraph.number_of_nodes()
        ch_matrix = CharacteristicMatrix(rballs_database, nodes_count, wl_iterations=4)
        ch_matrix.save_to_file(file_name)
        read_ch_matrix = CharacteristicMatrix.load_from_file(file_name)
        self.assertEqual(read_ch_matrix, ch_matrix, "The read characteristic matrix is different from the saved one.")
    
    def testCharacteristicMatrix_JaccardSimMatrix(self):
        dummy_hypergraph = Hypergraph(example_graphs.snm_dummy_graph)
        rballs_database, _ = similar_nodes_mining.extract_rballs_database(dummy_hypergraph, r_in=3, r_out=2, r_all=0)
        nodes_count = dummy_hypergraph.number_of_nodes()
        ch_matrix = CharacteristicMatrix(rballs_database, nodes_count, wl_iterations=0)
        ch_matrix_jaccard_sim = ch_matrix.compute_jaccard_similarity_matrix()
        equality = (self.ch_matrix_jaccard_sim_exp == ch_matrix_jaccard_sim).all()
        self.assertTrue(equality, "The computed Jaccard similarity matrix is wrong.")

    def testSimilarNodesMining(self):
        dummy_hypergraph = Hypergraph(example_graphs.snm_dummy_graph)
        rballs_database, _ = similar_nodes_mining.extract_rballs_database(dummy_hypergraph, r_in=3, r_out=2, r_all=0)
        nodes_count = dummy_hypergraph.number_of_nodes()
        ch_matrix = CharacteristicMatrix(rballs_database, nodes_count, wl_iterations=0)
        ch_matrix_jaccard_sim = ch_matrix.compute_jaccard_similarity_matrix()
        similarity_matrix_exp = np.array(ch_matrix_jaccard_sim >= 0.8, dtype=np.float32)
        sketch_matrix = SketchMatrix(25, 265, ch_matrix)
        similarity_matrix = similar_nodes_mining.get_node_similarity_matrix(sketch_matrix)
        equality = (similarity_matrix_exp == similarity_matrix).all()
        self.assertTrue(equality, "The computed similarity matrix is wrong (Keep in mind that the sketch_matrix is probabilistic, therefore, it may not be always correct. The test may pass in another run.).")
    
    def testSketchMatrix_ReadWrite(self):
        file_name = "test_files/sketch_matrix.tmp"
        dummy_hypergraph = Hypergraph(example_graphs.snm_dummy_graph)
        rballs_database, _ = similar_nodes_mining.extract_rballs_database(dummy_hypergraph, r_in=2, r_out=2, r_all=0)
        nodes_count = dummy_hypergraph.number_of_nodes()
        ch_matrix = CharacteristicMatrix(rballs_database, nodes_count, wl_iterations=4)
        sketch_matrix = SketchMatrix(5, 20, ch_matrix)
        sketch_matrix.save_to_file(file_name)
        read_sketch_matrix = SketchMatrix.load_from_file(file_name)
        equality = (read_sketch_matrix.matrix == sketch_matrix.matrix).all()
        self.assertTrue(equality, "The read sketch matrix is different from the saved one.")
    
    def testGetAllSimilarNodes(self):
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
        
        similar_nodes_1 = similar_nodes_mining.get_all_similar_nodes(dummy_sim_matrix_1, cols_nodes_map)
        similar_nodes_2 = similar_nodes_mining.get_all_similar_nodes(dummy_sim_matrix_2, cols_nodes_map)
        similar_nodes_3 = similar_nodes_mining.get_all_similar_nodes(dummy_sim_matrix_3, cols_nodes_map)
        self.assertEqual(similar_nodes_1_exp, similar_nodes_1, "Wrong similar nodes were extracted.")
        self.assertEqual(similar_nodes_2_exp, similar_nodes_2, "Wrong similar nodes were extracted.")
        self.assertEqual(similar_nodes_3_exp, similar_nodes_3, "Wrong similar nodes were extracted.")
    
    def testGetSimilarNodesToQueryNode(self):
        dummy_hypergraph = Hypergraph(example_graphs.snm_dummy_graph)
        rballs_database, _ = similar_nodes_mining.extract_rballs_database(dummy_hypergraph, r_in=3, r_out=2, r_all=0)
        nodes_count = dummy_hypergraph.number_of_nodes()
        ch_matrix = CharacteristicMatrix(rballs_database, nodes_count, wl_iterations=0)
        sketch_matrix = SketchMatrix(25, 265, ch_matrix)
        similar_nodes_exp = np.array([0, 5, 7])
        similar_nodes, _ = similar_nodes_mining.get_similar_nodes("n_7", dummy_hypergraph, sketch_matrix, 0, [], r_in=3, r_out=2, r_all=0)
        equality = similar_nodes_exp == similar_nodes
        if type(equality) is not bool:
            equality = equality.all()
        self.assertTrue(equality, "Wrong similar nodes were extracted (Keep in mind that the sketch_matrix is probabilistic, therefore, it may not be always correct. The test may pass in another run.).")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFeatureExtraction']
    unittest.main()