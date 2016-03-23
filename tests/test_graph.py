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
    
    def testRBallHyper_CenterDefaultColor(self):
        dummy_hypergraph = Hypergraph(example_graphs.gt_dummy_graph)
        rball_in = algorithms.r_ball_hyper(dummy_hypergraph, "n_10", 2, -1, center_default_color=True)
        rball_out = algorithms.r_ball_hyper(dummy_hypergraph, "n_10", 2, 1, center_default_color=True)
        rball_all = algorithms.r_ball_hyper(dummy_hypergraph, "n_10", 2, 0, center_default_color=True)
        d_rball_all = Hypergraph(example_graphs.gt_dummy_rball_10_r2_all)
        d_rball_out = Hypergraph(example_graphs.gt_dummy_rball_10_r2_out)
        d_rball_in = Hypergraph(example_graphs.gt_dummy_rball_10_r2_in)
        
        d_rball_all.node["n_10"]["labels"] = ["0"]
        d_rball_out.node["n_10"]["labels"] = ["0"]
        d_rball_in.node["n_10"]["labels"] = ["0"]
        
        all_isomorphic = algorithms.isomorphic(d_rball_all, rball_all)
        out_isomorphic = algorithms.isomorphic(d_rball_out, rball_out)
        in_isomorphic = algorithms.isomorphic(d_rball_in, rball_in)
        
        self.assertTrue(all_isomorphic, "Problem extracting r-ball with edge_dir=0.")
        self.assertTrue(out_isomorphic, "Problem extracting r-ball with edge_dir=1.")
        self.assertTrue(in_isomorphic, "Problem extracting r-ball with edge_dir=-1.")
    
    def testDropEdgesByProbability(self):
        dummy_hypergraph = Hypergraph(example_graphs.gt_dummy_graph)
        edges_count = dummy_hypergraph.number_of_edges()
        for p in [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.]:
            new_hypergraph = algorithms.drop_edges_by_probability(dummy_hypergraph, p)
            new_graph = algorithms.drop_edges_by_probability(example_graphs.gt_dummy_graph, p)
            edges_prop_exp = ((1. - p) * edges_count) / float(edges_count)
            edges_prop_hyper = float(new_hypergraph.number_of_edges()) / float(edges_count)
            edges_prop = float(new_graph.number_of_edges()) / float(edges_count)
            msg = "The proportion of edges remaining after being dropping deviate too much from the expected."
            self.assertAlmostEquals(edges_prop_exp, edges_prop_hyper, delta=0.2, msg=msg)
            self.assertAlmostEquals(edges_prop_exp, edges_prop, delta=0.2, msg=msg)
    
    def testRDFToNxGraphConvertionWithColoring(self):
        dummy_colored, _ = rdf.convert_rdf_to_nx_graph(["test_files/dummy.rdf"], test_mode=True)
        isomorphic = algorithms.isomorphic(example_graphs.gt_dummy_colored_expected, dummy_colored)
        self.assertTrue(isomorphic, "Problem converting RDF graph to Networkx graph with colors.")
    
    def testWeisfeilerLehman(self):
        wl_state_exp = {
            "labels": {
                "0": "wl_0.0",
                "1": "wl_0.1",
                "a": "wl_0.2",
                "b": "wl_0.3",
                "wl_0.0;in(wl_0.3)": "wl_1.0",
                "wl_0.0;any(wl_0.2),in(wl_0.2)": "wl_1.1",
                "wl_0.1;any(wl_0.2),out(wl_0.2,wl_0.3)": "wl_1.2",
                "wl_0.1;any(wl_0.2),out(wl_0.2)": "wl_1.3",
                "wl_0.2;in(wl_0.1),out(wl_0.0)": "wl_1.4",
                "wl_0.2;any(wl_0.0,wl_0.1)": "wl_1.5",
                "wl_0.3;in(wl_0.1),out(wl_0.0)": "wl_1.6",
                "wl_1.0;in(wl_1.6)": "wl_2.0",
                "wl_1.1;any(wl_1.5),in(wl_1.4)": "wl_2.1",
                "wl_1.2;any(wl_1.5),out(wl_1.4,wl_1.6)": "wl_2.2",
                "wl_1.3;any(wl_1.5),out(wl_1.4)": "wl_2.3",
                "wl_1.4;in(wl_1.2),out(wl_1.1)": "wl_2.4",
                "wl_1.4;in(wl_1.3),out(wl_1.1)": "wl_2.5",
                "wl_1.5;any(wl_1.1,wl_1.2)": "wl_2.6",
                "wl_1.5;any(wl_1.1,wl_1.3)": "wl_2.7",
                "wl_1.6;in(wl_1.2),out(wl_1.0)": "wl_2.8",
                "wl_2.0;in(wl_2.8)": "wl_3.0",
                "wl_2.1;any(wl_2.7),in(wl_2.4)": "wl_3.1",
                "wl_2.1;any(wl_2.6),in(wl_2.5)": "wl_3.2",
                "wl_2.2;any(wl_2.6),out(wl_2.4,wl_2.8)": "wl_3.3",
                "wl_2.3;any(wl_2.7),out(wl_2.5)": "wl_3.4",
                "wl_2.4;in(wl_2.2),out(wl_2.1)": "wl_3.5",
                "wl_2.5;in(wl_2.3),out(wl_2.1)": "wl_3.6",
                "wl_2.6;any(wl_2.1,wl_2.2)": "wl_3.7",
                "wl_2.7;any(wl_2.1,wl_2.3)": "wl_3.8",
                "wl_2.8;in(wl_2.2),out(wl_2.0)": "wl_3.9"
            },
            "next_labels": {
                0: 4,
                1: 7,
                2: 9,
                3: 10
            }
        }
        hyper_dummy_wl = Hypergraph(example_graphs.gt_dummy_wl)
        hyper_dummy_wl, wl_state = weisfeiler_lehman.init(hyper_dummy_wl, test_mode=True)
        i = 1
        while True:
            new_hyper_dummy_wl, wl_state = weisfeiler_lehman.iterate(hyper_dummy_wl, wl_state, i, test_mode=True)
            if weisfeiler_lehman.is_stable(hyper_dummy_wl, new_hyper_dummy_wl, i):
                break
            hyper_dummy_wl = new_hyper_dummy_wl
            i += 1
        self.assertEqual(wl_state_exp, wl_state, "The multi-sets of labels computed by Weisfeiler-Lehman are not correct.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testHypergraphReadWrite']
    unittest.main()