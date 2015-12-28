'''
Created on Dec 18, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import algorithms, rdf
import networkx as nx
import unittest

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
    
    dummy_subgraph = nx.MultiDiGraph()
    dummy_subgraph.add_node(1, labels = ["1"])
    dummy_subgraph.add_node(6, labels = ["6"])
    dummy_subgraph.add_node(9, labels = ["9"])
    dummy_subgraph.add_node(10, labels = ["10"])
    dummy_subgraph.add_edge(1, 6, label = "0")
    dummy_subgraph.add_edge(1, 9, label = "0")
    dummy_subgraph.add_edge(6, 10, label = "0")
    
    # r-ball: center=10, r=2, edge_dir=0
    dummy_rball_10_r2_all = nx.MultiDiGraph()
    dummy_rball_10_r2_all.add_node(10, labels = ["10"]) # center
    dummy_rball_10_r2_all.add_node(1, labels = ["1"])
    dummy_rball_10_r2_all.add_node(3, labels = ["3"])
    dummy_rball_10_r2_all.add_node(4, labels = ["4"])
    dummy_rball_10_r2_all.add_node(5, labels = ["5"])
    dummy_rball_10_r2_all.add_node(6, labels = ["6"])
    dummy_rball_10_r2_all.add_node(11, labels = ["11"])
    dummy_rball_10_r2_all.add_node(12, labels = ["12"])
    dummy_rball_10_r2_all.add_node(13, labels = ["13"])
    dummy_rball_10_r2_all.add_node(16, labels = ["16"])
    dummy_rball_10_r2_all.add_edge(1, 3, label = "0")
    dummy_rball_10_r2_all.add_edge(1, 6, label = "0")
    dummy_rball_10_r2_all.add_edge(3, 4, label = "0")
    dummy_rball_10_r2_all.add_edge(3, 10, label = "0")
    dummy_rball_10_r2_all.add_edge(3, 11, label = "0")
    dummy_rball_10_r2_all.add_edge(3, 12, label = "0")
    dummy_rball_10_r2_all.add_edge(5, 6, label = "0")
    dummy_rball_10_r2_all.add_edge(6, 10, label = "0")
    dummy_rball_10_r2_all.add_edge(6, 16, label = "0")
    dummy_rball_10_r2_all.add_edge(10, 11, label = "0")
    dummy_rball_10_r2_all.add_edge(11, 12, label = "0")
    dummy_rball_10_r2_all.add_edge(11, 13, label = "0")
    
    # r-ball: center=10, r=2, edge_dir=1
    dummy_rball_10_r2_out = nx.MultiDiGraph()
    dummy_rball_10_r2_out.add_node(10, labels = ["10"]) # center
    dummy_rball_10_r2_out.add_node(11, labels = ["11"])
    dummy_rball_10_r2_out.add_node(12, labels = ["12"])
    dummy_rball_10_r2_out.add_node(13, labels = ["13"])
    dummy_rball_10_r2_out.add_edge(10, 11, label = "0")
    dummy_rball_10_r2_out.add_edge(11, 12, label = "0")
    dummy_rball_10_r2_out.add_edge(11, 13, label = "0")
    
    # r-ball: center=10, r=2, edge_dir=-1
    dummy_rball_10_r2_in = nx.MultiDiGraph()
    dummy_rball_10_r2_in.add_node(10, labels = ["10"]) # center
    dummy_rball_10_r2_in.add_node(1, labels = ["1"])
    dummy_rball_10_r2_in.add_node(3, labels = ["3"])
    dummy_rball_10_r2_in.add_node(5, labels = ["5"])
    dummy_rball_10_r2_in.add_node(6, labels = ["6"])
    dummy_rball_10_r2_in.add_edge(1, 3, label = "0")
    dummy_rball_10_r2_in.add_edge(1, 6, label = "0")
    dummy_rball_10_r2_in.add_edge(3, 10, label = "0")
    dummy_rball_10_r2_in.add_edge(5, 6, label = "0")
    dummy_rball_10_r2_in.add_edge(6, 10, label = "0")
    
    dummy_colored_expected = nx.MultiDiGraph()
    dummy_colored_expected.add_node("1", labels=["4"])
    dummy_colored_expected.add_node("2", labels=["5", "6"])
    dummy_colored_expected.add_node("3", labels=["2", "3"])
    dummy_colored_expected.add_edge("2", "3", label="7")
    
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
    
    def testHypergraph_edges_iter(self):
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        self.assertEqual(len(list(dummy_hypergraph.edges_iter())), 32)
        self.assertEqual(set(dummy_hypergraph.edges_iter("n_6")), set(["e_5", "e_9", "e_13", "e_28"]))
        self.assertEqual(set(dummy_hypergraph.edges_iter("n_5", "n_1")), set(["e_15"]))
    
    def testHypergraph_subgraph_with_labels(self):
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        subgraph = dummy_hypergraph.subgraph_with_labels(set(["n_1", "n_6", "n_9", "n_10"]))
        isomorphic = nx.is_isomorphic(self.dummy_subgraph, subgraph)
        self.assertTrue(isomorphic, "Incorrect subgraph extraction from hypergraph.")
    
    def testRBallHyper(self):
        dummy_hypergraph = Hypergraph(self.dummy_graph)
        rball_in = algorithms.r_ball_hyper(dummy_hypergraph, "n_10", 2, -1)
        rball_out = algorithms.r_ball_hyper(dummy_hypergraph, "n_10", 2, 1)
        rball_all = algorithms.r_ball_hyper(dummy_hypergraph, "n_10", 2, 0)
        d_rball_all = Hypergraph(self.dummy_rball_10_r2_all)
        d_rball_out = Hypergraph(self.dummy_rball_10_r2_out)
        d_rball_in = Hypergraph(self.dummy_rball_10_r2_in)
        
        all_isomorphic = nx.is_isomorphic(d_rball_all.bipartite_graph, rball_all.bipartite_graph)
        out_isomorphic = nx.is_isomorphic(d_rball_out.bipartite_graph, rball_out.bipartite_graph)
        in_isomorphic = nx.is_isomorphic(d_rball_in.bipartite_graph, rball_in.bipartite_graph)
        
        self.assertTrue(all_isomorphic, "Problem extracting r-ball with edge_dir=0.")
        self.assertTrue(out_isomorphic, "Problem extracting r-ball with edge_dir=1.")
        self.assertTrue(in_isomorphic, "Problem extracting r-ball with edge_dir=-1.")
    
    def testRDFToNxGraphConvertionWithColoring(self):
        dummy_colored, _ = rdf.convert_rdf_to_nx_graph(["test_files/dummy.rdf"], test_mode=True)
        isomorphic = nx.is_isomorphic(self.dummy_colored_expected, dummy_colored)
        self.assertTrue(isomorphic, "Problem converting RDF graph to Networkx graph with colors.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testHypergraphReadWrite']
    unittest.main()