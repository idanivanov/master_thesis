'''
Created on Dec 18, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms import weisfeiler_lehman
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import algorithms, rdf
from tests import example_graphs
import unittest

class TestGraph(unittest.TestCase):
    def testHypergraph_Copy(self):
        dummy_hypergraph = Hypergraph(example_graphs.gt_dummy_graph)
        dummy_copy = dummy_hypergraph.copy()
        self.assertEqual(dummy_hypergraph, dummy_copy, "The copy was not correct.")

    def testHypergraph_ReadWrite(self):
        file_name = "test_files/dummy_hypergraph.tmp"
        dummy_hypergraph = Hypergraph(example_graphs.gt_dummy_graph)
        dummy_hypergraph.save_to_file(file_name)
        read_hypergraph = Hypergraph.load_from_file(file_name)
        self.assertEqual(dummy_hypergraph, read_hypergraph, "The read hypergraph is different from the saved one.")
    
    def testHypergraph_edges_iter(self):
        dummy_hypergraph = Hypergraph(example_graphs.gt_dummy_graph)
        self.assertEqual(len(list(dummy_hypergraph.edges_iter())), 32)
        self.assertEqual(set(dummy_hypergraph.edges_iter("n_6")), set(["e_5", "e_9", "e_13", "e_28"]))
        self.assertEqual(set(dummy_hypergraph.edges_iter("n_5", "n_1")), set(["e_15"]))
    
    def testHypergraph_subgraph_with_labels(self):
        dummy_hypergraph = Hypergraph(example_graphs.gt_dummy_graph)
        subgraph = dummy_hypergraph.subgraph_with_labels(set(["n_1", "n_6", "n_9", "n_10"]))
        isomorphic = algorithms.isomorphic(example_graphs.gt_dummy_subgraph, subgraph)
        self.assertTrue(isomorphic, "Incorrect subgraph extraction from hypergraph.")
    
    def testRBallHyper(self):
        dummy_hypergraph = Hypergraph(example_graphs.gt_dummy_graph)
        rball_in = algorithms.r_ball_hyper(dummy_hypergraph, "n_10", 2, -1)
        rball_out = algorithms.r_ball_hyper(dummy_hypergraph, "n_10", 2, 1)
        rball_all = algorithms.r_ball_hyper(dummy_hypergraph, "n_10", 2, 0)
        d_rball_all = Hypergraph(example_graphs.gt_dummy_rball_10_r2_all)
        d_rball_out = Hypergraph(example_graphs.gt_dummy_rball_10_r2_out)
        d_rball_in = Hypergraph(example_graphs.gt_dummy_rball_10_r2_in)
        
        all_isomorphic = algorithms.isomorphic(d_rball_all, rball_all)
        out_isomorphic = algorithms.isomorphic(d_rball_out, rball_out)
        in_isomorphic = algorithms.isomorphic(d_rball_in, rball_in)
        
        self.assertTrue(all_isomorphic, "Problem extracting r-ball with edge_dir=0.")
        self.assertTrue(out_isomorphic, "Problem extracting r-ball with edge_dir=1.")
        self.assertTrue(in_isomorphic, "Problem extracting r-ball with edge_dir=-1.")
    
    def testRDFToNxGraphConvertionWithColoring(self):
        dummy_colored, _ = rdf.convert_rdf_to_nx_graph(["test_files/dummy.rdf"], test_mode=True)
        isomorphic = algorithms.isomorphic(example_graphs.gt_dummy_colored_expected, dummy_colored)
        self.assertTrue(isomorphic, "Problem converting RDF graph to Networkx graph with colors.")
    
    def testWeisfeilerLehman(self):
        labels_list_exp = [
            '0', '1', 'a', 'b',
            'wl_0;any(wl_2),in(wl_2)', 'wl_0;in(wl_3)', 'wl_1;any(wl_2),out(wl_2)', 'wl_1;any(wl_2),out(wl_2,wl_3)', 'wl_2;any(wl_0,wl_1)', 'wl_2;in(wl_1),out(wl_0)', 'wl_3;in(wl_1),out(wl_0)',
            'wl_10;in(wl_7),out(wl_5)', 'wl_4;any(wl_8),in(wl_9)', 'wl_5;in(wl_10)', 'wl_6;any(wl_8),out(wl_9)', 'wl_7;any(wl_8),out(wl_10,wl_9)', 'wl_8;any(wl_4,wl_6)', 'wl_8;any(wl_4,wl_7)', 'wl_9;in(wl_6),out(wl_4)', 'wl_9;in(wl_7),out(wl_4)',
            'wl_11;in(wl_15),out(wl_13)', 'wl_12;any(wl_16),in(wl_19)', 'wl_12;any(wl_17),in(wl_18)', 'wl_13;in(wl_11)', 'wl_14;any(wl_16),out(wl_18)', 'wl_15;any(wl_17),out(wl_11,wl_19)', 'wl_16;any(wl_12,wl_14)', 'wl_17;any(wl_12,wl_15)', 'wl_18;in(wl_14),out(wl_12)', 'wl_19;in(wl_15),out(wl_12)',
            'wl_20;in(wl_25),out(wl_23)', 'wl_21;any(wl_26),in(wl_29)', 'wl_22;any(wl_27),in(wl_28)', 'wl_23;in(wl_20)', 'wl_24;any(wl_26),out(wl_28)', 'wl_25;any(wl_27),out(wl_20,wl_29)', 'wl_26;any(wl_21,wl_24)', 'wl_27;any(wl_22,wl_25)', 'wl_28;in(wl_24),out(wl_22)', 'wl_29;in(wl_25),out(wl_21)'
        ]
        hyper_dummy_wl = Hypergraph(example_graphs.gt_dummy_wl)
        hyper_dummy_wl, labels_list = weisfeiler_lehman.init(hyper_dummy_wl)
        i = 1
        while True:
            new_hyper_dummy_wl, labels_list = weisfeiler_lehman.iterate(hyper_dummy_wl, labels_list)
            if weisfeiler_lehman.is_stable(hyper_dummy_wl, new_hyper_dummy_wl, i):
                break
            hyper_dummy_wl = new_hyper_dummy_wl
            i += 1
        self.assertEqual(labels_list_exp, labels_list, "The multi-sets of labels computed by Weisfeiler-Lehman are not correct.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testHypergraphReadWrite']
    unittest.main()