'''
Created on Dec 28, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.arnborg_proskurowski.reducible_feature import ReducibleFeature
from ivanov.graph.algorithms import arnborg_proskurowski
import networkx as nx
import unittest

class TestArnborgProskurowski(unittest.TestCase):

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
    
    ring_graph = nx.MultiDiGraph()
    ring_graph.add_node(1, labels=["1"])
    ring_graph.add_node(2, labels=["2"])
    ring_graph.add_node(3, labels=["3"])
    ring_graph.add_node(4, labels=["4"])
    ring_graph.add_node(5, labels=["5"])
    ring_graph.add_edge(1, 2, label="a")
    ring_graph.add_edge(2, 3, label="b")
    ring_graph.add_edge(3, 4, label="c")
    ring_graph.add_edge(4, 5, label="d")
    ring_graph.add_edge(5, 1, label="e")
    
    graph_tw_3 = nx.MultiDiGraph()
    # base structure
    graph_tw_3.add_node(201, labels=["base_1"])
    graph_tw_3.add_node(202, labels=["base_2"])
    graph_tw_3.add_node(203, labels=["base_3"])
    graph_tw_3.add_node(204, labels=["base_4"])
    graph_tw_3.add_edge(201, 202, label="0")
    graph_tw_3.add_edge(201, 203, label="0")
    graph_tw_3.add_edge(201, 204, label="0")
    graph_tw_3.add_edge(202, 203, label="0")
    graph_tw_3.add_edge(202, 204, label="0")
    graph_tw_3.add_edge(203, 204, label="0")
    # rule 4.1
    graph_tw_3.add_node(1, labels=["1 (4.1)"])
    graph_tw_3.add_edge(1, 202, label="0")
    graph_tw_3.add_edge(1, 203, label="0")
    graph_tw_3.add_edge(1, 204, label="0")
    # rule 4.2
    graph_tw_3.add_node(5, labels=["1 (4.2)"])
    graph_tw_3.add_node(6, labels=["2 (4.2)"])
    graph_tw_3.add_node(7, labels=["3 (4.2)"])
    graph_tw_3.add_node(8, labels=["4 (4.2)"])
    graph_tw_3.add_node(9, labels=["5 (4.2)"])
    graph_tw_3.add_edge(5, 7, label="0")
    graph_tw_3.add_edge(5, 8, label="0")
    graph_tw_3.add_edge(5, 9, label="0")
    graph_tw_3.add_edge(6, 7, label="0")
    graph_tw_3.add_edge(6, 8, label="0")
    graph_tw_3.add_edge(6, 9, label="0")
    graph_tw_3.add_edge(7, 201, label="0")
    graph_tw_3.add_edge(8, 202, label="0")
    graph_tw_3.add_edge(9, 203, label="0")
    # rule 4.3
    graph_tw_3.add_node(220, labels=["0"])
    graph_tw_3.add_node(221, labels=["0"])
    graph_tw_3.add_node(222, labels=["0"])
    graph_tw_3.add_node(223, labels=["G"])
    graph_tw_3.add_node(230, labels=["0"])
    graph_tw_3.add_node(231, labels=["0"])
    graph_tw_3.add_node(232, labels=["0"])
    graph_tw_3.add_node(233, labels=["G"])
    graph_tw_3.add_node(240, labels=["0"])
    graph_tw_3.add_node(241, labels=["0"])
    graph_tw_3.add_node(242, labels=["0"])
    graph_tw_3.add_node(243, labels=["G"])
    graph_tw_3.add_edge(220, 221, label="n")
    graph_tw_3.add_edge(220, 222, label="n")
    graph_tw_3.add_edge(220, 223, label="n")
    graph_tw_3.add_edge(221, 222, label="n")
    graph_tw_3.add_edge(221, 223, label="n")
    graph_tw_3.add_edge(222, 223, label="n")
    graph_tw_3.add_edge(230, 231, label="n")
    graph_tw_3.add_edge(230, 232, label="n")
    graph_tw_3.add_edge(230, 233, label="n")
    graph_tw_3.add_edge(231, 232, label="n")
    graph_tw_3.add_edge(231, 233, label="n")
    graph_tw_3.add_edge(232, 233, label="n")
    graph_tw_3.add_edge(240, 241, label="n")
    graph_tw_3.add_edge(240, 242, label="n")
    graph_tw_3.add_edge(240, 243, label="n")
    graph_tw_3.add_edge(241, 242, label="n")
    graph_tw_3.add_edge(241, 243, label="n")
    graph_tw_3.add_edge(242, 243, label="n")
    graph_tw_3.add_node(250, labels=["G"]) # hub
    graph_tw_3.add_node(251, labels=["0"])
    graph_tw_3.add_node(252, labels=["0"])
    graph_tw_3.add_node(253, labels=["0"])
    graph_tw_3.add_edge(250, 251, label="n")
    graph_tw_3.add_edge(250, 252, label="n")
    graph_tw_3.add_edge(250, 253, label="n")
    graph_tw_3.add_edge(251, 223, label="n")
    graph_tw_3.add_edge(251, 243, label="n")
    graph_tw_3.add_edge(252, 223, label="n")
    graph_tw_3.add_edge(252, 233, label="n")
    graph_tw_3.add_edge(253, 233, label="n")
    graph_tw_3.add_edge(253, 243, label="n")
    # rule 5.1.1
    graph_tw_3.add_node(17, labels=["1 (5.1.1)"])
    graph_tw_3.add_node(18, labels=["2 (5.1.1)"])
    graph_tw_3.add_node(19, labels=["3 (5.1.1)"])
    graph_tw_3.add_node(20, labels=["4 (5.1.1)"])
    graph_tw_3.add_edge(17, 18, label="0")
    graph_tw_3.add_edge(17, 19, label="0")
    graph_tw_3.add_edge(17, 20, label="0")
    graph_tw_3.add_edge(18, 19, label="0")
    graph_tw_3.add_edge(18, 20, label="0")
    graph_tw_3.add_edge(19, 20, label="0")
    # rule 5.1.2
    graph_tw_3.add_node(21, labels=["1 (5.1.2)"])
    graph_tw_3.add_node(22, labels=["2 (5.1.2)"])
    graph_tw_3.add_node(23, labels=["3 (5.1.2)"])
    graph_tw_3.add_node(24, labels=["4 (5.1.2)"])
    graph_tw_3.add_edge(21, 22, label="0")
    graph_tw_3.add_edge(21, 23, label="0")
    graph_tw_3.add_edge(21, 24, label="0")
    graph_tw_3.add_edge(22, 23, label="0")
    graph_tw_3.add_edge(22, 24, label="0")
    graph_tw_3.add_edge(23, 201, label="0")
    graph_tw_3.add_edge(24, 202, label="0")
    graph_tw_3.add_edge(23, 202, label="0")
    graph_tw_3.add_edge(24, 201, label="0")
    # rule 5.2.1 - 1
    graph_tw_3.add_node(31, labels=["1 (5.2.1 - 1)"])
    graph_tw_3.add_node(32, labels=["2 (5.2.1 - 1)"])
    graph_tw_3.add_edge(31, 32, label="0")
    graph_tw_3.add_edge(31, 202, label="0")
    graph_tw_3.add_edge(31, 203, label="0")
    graph_tw_3.add_edge(32, 202, label="0")
    graph_tw_3.add_edge(32, 204, label="0")
#     # rule 5.2.1 - 2 # This configuration is not safely reducible
#     graph_tw_3.add_node(41, labels=["1 (5.2.1 - 2)"])
#     graph_tw_3.add_node(42, labels=["2 (5.2.1 - 2)"])
#     graph_tw_3.add_edge(41, 42, label="0")
#     graph_tw_3.add_edge(41, 201, label="0")
#     graph_tw_3.add_edge(41, 202, label="0")
#     graph_tw_3.add_edge(42, 203, label="0")
#     graph_tw_3.add_edge(42, 204, label="0")
    # rule 5.2.2
    graph_tw_3.add_node(51, labels=["1 (5.2.2)"])
    graph_tw_3.add_node(52, labels=["2 (5.2.2)"])
    graph_tw_3.add_node(53, labels=["3 (5.2.2)"])
    graph_tw_3.add_node(54, labels=["4 (5.2.2)"])
    graph_tw_3.add_edge(51, 52, label="0")
    graph_tw_3.add_edge(51, 53, label="0")
    graph_tw_3.add_edge(51, 204, label="0")
    graph_tw_3.add_edge(52, 54, label="0")
    graph_tw_3.add_edge(52, 204, label="0")
    graph_tw_3.add_edge(53, 204, label="0")
    graph_tw_3.add_edge(54, 204, label="0")
    graph_tw_3.add_edge(53, 202, label="0")
    graph_tw_3.add_edge(54, 203, label="0")
    # rule 5.2.3.1
    graph_tw_3.add_node(60, labels=["0 (5.2.3.1)"])
    graph_tw_3.add_node(61, labels=["1 (5.2.3.1)"])
    graph_tw_3.add_node(62, labels=["2 (5.2.3.1)"])
    graph_tw_3.add_node(63, labels=["3 (5.2.3.1)"])
    graph_tw_3.add_node(64, labels=["4 (5.2.3.1)"])
    graph_tw_3.add_node(65, labels=["5 (5.2.3.1)"])
    graph_tw_3.add_edge(60, 61, label="0")
    graph_tw_3.add_edge(60, 62, label="0")
    graph_tw_3.add_edge(60, 63, label="0")
    graph_tw_3.add_edge(60, 64, label="0")
    graph_tw_3.add_edge(60, 65, label="0")
    graph_tw_3.add_edge(61, 62, label="0")
    graph_tw_3.add_edge(62, 63, label="0")
    graph_tw_3.add_edge(63, 64, label="0")
    graph_tw_3.add_edge(64, 65, label="0")
    graph_tw_3.add_edge(65, 61, label="0")
#     # rule 5.2.3.2 # TODO: not sure what is this configuration
#     graph_tw_3.add_node(, labels=[" (5.2.3.2)"])
#     graph_tw_3.add_edge(, , label="0")
    # rule 5.2.3.3
    graph_tw_3.add_node(81, labels=["1 (5.2.3.3)"])
    graph_tw_3.add_node(82, labels=["2 (5.2.3.3)"])
    graph_tw_3.add_node(83, labels=["3 (5.2.3.3)"])
    graph_tw_3.add_node(84, labels=["4 (5.2.3.3)"])
    graph_tw_3.add_edge(81, 82, label="0")
    graph_tw_3.add_edge(81, 83, label="0")
    graph_tw_3.add_edge(81, 201, label="0")
    graph_tw_3.add_edge(82, 84, label="0")
    graph_tw_3.add_edge(82, 202, label="0")
    graph_tw_3.add_edge(83, 84, label="0")
    graph_tw_3.add_edge(83, 201, label="0")
    graph_tw_3.add_edge(84, 202, label="0")
    # rule 5.2.4
    graph_tw_3.add_node(121, labels=["0"])
    graph_tw_3.add_node(122, labels=["0"])
    graph_tw_3.add_node(123, labels=["0"])
    graph_tw_3.add_node(124, labels=["0"])
    graph_tw_3.add_node(125, labels=["0"])
    graph_tw_3.add_node(126, labels=["0"])
    graph_tw_3.add_node(127, labels=["0"])
    graph_tw_3.add_node(128, labels=["0"])
    graph_tw_3.add_edge(121, 141, label="n")
    graph_tw_3.add_edge(121, 122, label="n")
    graph_tw_3.add_edge(121, 123, label="n")
    graph_tw_3.add_edge(122, 123, label="n")
    graph_tw_3.add_edge(122, 124, label="n")
    graph_tw_3.add_edge(123, 124, label="n")
    graph_tw_3.add_edge(124, 125, label="n")
    graph_tw_3.add_edge(125, 126, label="n")
    graph_tw_3.add_edge(125, 127, label="n")
    graph_tw_3.add_edge(126, 127, label="n")
    graph_tw_3.add_edge(126, 128, label="n")
    graph_tw_3.add_edge(127, 128, label="n")
    graph_tw_3.add_edge(128, 142, label="n")
    # rule 5.2.5
    graph_tw_3.add_node(131, labels=["1 (5.2.5)"])
    graph_tw_3.add_node(132, labels=["2 (5.2.5)"])
    graph_tw_3.add_node(133, labels=["3 (5.2.5)"])
    graph_tw_3.add_node(134, labels=["4 (5.2.5)"])
    graph_tw_3.add_node(135, labels=["5 (5.2.5)"])
    graph_tw_3.add_node(136, labels=["6 (5.2.5)"])
    graph_tw_3.add_edge(131, 132, label="0")
    graph_tw_3.add_edge(131, 133, label="0")
    graph_tw_3.add_edge(131, 134, label="0")
    graph_tw_3.add_edge(132, 133, label="0")
    graph_tw_3.add_edge(132, 135, label="0")
    graph_tw_3.add_edge(133, 136, label="0")
    graph_tw_3.add_edge(134, 135, label="0")
    graph_tw_3.add_edge(134, 136, label="0")
    graph_tw_3.add_edge(135, 136, label="0")
    # rule 6.1
    graph_tw_3.add_node(141, labels=["1 (6.1)"])
    graph_tw_3.add_node(142, labels=["2 (6.1)"])
    graph_tw_3.add_node(143, labels=["3 (6.1)"])
    graph_tw_3.add_node(144, labels=["4 (6.1)"])
    graph_tw_3.add_node(145, labels=["5 (6.1)"])
    graph_tw_3.add_node(146, labels=["6 (6.1)"])
    graph_tw_3.add_edge(141, 142, label="0")
    graph_tw_3.add_edge(141, 144, label="0")
    graph_tw_3.add_edge(141, 146, label="0")
    graph_tw_3.add_edge(142, 143, label="0")
    graph_tw_3.add_edge(142, 145, label="0")
    graph_tw_3.add_edge(143, 144, label="0")
    graph_tw_3.add_edge(143, 146, label="0")
    graph_tw_3.add_edge(144, 145, label="0")
    graph_tw_3.add_edge(145, 146, label="0")
    # rule 6.2
    graph_tw_3.add_node(151, labels=["1 (6.2)"])
    graph_tw_3.add_node(152, labels=["2 (6.2)"])
    graph_tw_3.add_node(154, labels=["4 (6.2)"])
    graph_tw_3.add_node(155, labels=["5 (6.2)"])
    graph_tw_3.add_edge(151, 152, label="0")
    graph_tw_3.add_edge(151, 154, label="0")
    graph_tw_3.add_edge(151, 204, label="0")
    graph_tw_3.add_edge(152, 203, label="0")
    graph_tw_3.add_edge(152, 155, label="0")
    graph_tw_3.add_edge(203, 154, label="0")
    graph_tw_3.add_edge(154, 155, label="0")
    graph_tw_3.add_edge(155, 204, label="0")
    # rule 7.1
    graph_tw_3.add_node(161, labels=["1 (7.1)"])
    graph_tw_3.add_node(162, labels=["2 (7.1)"])
    graph_tw_3.add_node(163, labels=["3 (7.1)"])
    graph_tw_3.add_node(164, labels=["4 (7.1)"])
    graph_tw_3.add_node(165, labels=["5 (7.1)"])
    graph_tw_3.add_node(166, labels=["6 (7.1)"])
    graph_tw_3.add_node(167, labels=["7 (7.1)"])
    graph_tw_3.add_node(168, labels=["8 (7.1)"])
    graph_tw_3.add_edge(161, 162, label="0")
    graph_tw_3.add_edge(161, 163, label="0")
    graph_tw_3.add_edge(161, 165, label="0")
    graph_tw_3.add_edge(162, 164, label="0")
    graph_tw_3.add_edge(162, 166, label="0")
    graph_tw_3.add_edge(163, 164, label="0")
    graph_tw_3.add_edge(163, 167, label="0")
    graph_tw_3.add_edge(164, 168, label="0")
    graph_tw_3.add_edge(165, 166, label="0")
    graph_tw_3.add_edge(165, 167, label="0")
    graph_tw_3.add_edge(166, 168, label="0")
    graph_tw_3.add_edge(167, 168, label="0")
    # rule 7.2 # TODO: reduced as 7.1 because it has lower priority
    graph_tw_3.add_node(171, labels=["1 (7.2)"])
    graph_tw_3.add_node(172, labels=["2 (7.2)"])
    graph_tw_3.add_node(173, labels=["3 (7.2)"])
    graph_tw_3.add_node(175, labels=["5 (7.2)"])
    graph_tw_3.add_node(176, labels=["6 (7.2)"])
    graph_tw_3.add_node(177, labels=["7 (7.2)"])
    graph_tw_3.add_edge(171, 172, label="0")
    graph_tw_3.add_edge(171, 173, label="0")
    graph_tw_3.add_edge(171, 175, label="0")
    graph_tw_3.add_edge(172, 202, label="0")
    graph_tw_3.add_edge(172, 176, label="0")
    graph_tw_3.add_edge(173, 202, label="0")
    graph_tw_3.add_edge(173, 177, label="0")
    graph_tw_3.add_edge(175, 176, label="0")
    graph_tw_3.add_edge(175, 177, label="0")
    graph_tw_3.add_edge(176, 203, label="0")
    graph_tw_3.add_edge(177, 203, label="0")
    
    def common_asserts(self, tw, tw_exp, canon_str, canon_str_exp, features, features_exp):
        self.assertEqual(tw, tw_exp, "The tree-width was not estimated correctly.")
        self.assertEqual(canon_str, canon_str_exp, "The canonical string was not extracted correctly.")
        self.assertEqual(features, features_exp, "The features were not extracted correctly.")

    def testTW_2(self):
        features_exp = [
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
        canon_str_exp = "(1.1;(0.1;(0),(1.2;(0,((0,1),(1,0))),(0))),((0.2;((2.1;((0.2;((2.1;(0,((0,1),(1,0))),(0),(0,((0,1),(1,0)))),((0,1),(1,0))),(0,((0,1),(1,0)))),((0,1),(1,0))),(0.1;(0),(1.2;(0,((0,1),(1,0))),(0))),(0,((0,1),(1,0)))),((0,1))),((2.1;(0,((0,1),(1,0))),(0.1;(0.1;(0),(1.2;(0,((0,1),(1,0))),(0))),(2.1;(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))))),(0,((0,1),(1,0)))),((0,1),(1,0))),(0,((0,1),(1,0)))),((0,1))),(0.1;(0.1;(0),(1.2;(0,((0,1),(1,0))),(0))),(2.1;(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))),(0),(0,((0,1),(1,0))))))"
        tw, canon_str, features = arnborg_proskurowski.run_algorithm(self.graph_tw_2, return_features=True)
        self.common_asserts(tw, 2, canon_str, canon_str_exp, features, features_exp)
        tw_1 = arnborg_proskurowski.get_treewidth(self.graph_tw_2)
        canon_str_1 = arnborg_proskurowski.get_canonical_representation(self.graph_tw_2)
        features_1 = arnborg_proskurowski.get_reduced_features(self.graph_tw_2)
        self.common_asserts(tw_1, 2, canon_str_1, canon_str_exp, features_1, features_exp)
     
    def testTW_2_ring(self):
        features_exp = [
            ReducibleFeature(2, 2, ["n_1"], ["n_2", "n_3", "n_4", "n_5"]),
        ]
        canon_str_exp = "(2.2;1,(a,((0,1))),2,(b,((0,1))),3,(c,((0,1))),4,(d,((0,1))),5,(e,((0,1))))"
        tw, canon_str, features = arnborg_proskurowski.run_algorithm(self.ring_graph, return_features=True)
        self.common_asserts(tw, 2, canon_str, canon_str_exp, features, features_exp)
        tw_1 = arnborg_proskurowski.get_treewidth(self.ring_graph)
        canon_str_1 = arnborg_proskurowski.get_canonical_representation(self.ring_graph)
        features_1 = arnborg_proskurowski.get_reduced_features(self.ring_graph)
        self.common_asserts(tw_1, 2, canon_str_1, canon_str_exp, features_1, features_exp)
    
    def testTW_3(self):
        features_exp = [
            ReducibleFeature(4, 1, [u'n_1'], [u'n_202', u'n_203', u'n_204'], 0, 0),
            ReducibleFeature(4, 2, [u'n_5', u'n_6'], [u'n_7', u'n_8', u'n_9'], 0, 0),
            ReducibleFeature(4, 3, set([u'n_253', u'n_252', u'n_251']), set([u'n_223', u'n_233', u'n_250', u'n_243']), 0, 0),
            ReducibleFeature(4, 1, [u'n_250'], [u'n_223', u'n_233', u'n_243'], 0, 0),
            ReducibleFeature(5, 1, set([u'n_231', u'n_230', u'n_232']), set([u'n_233']), 1, 0),
            ReducibleFeature(5, 1, set([u'n_22', u'n_21']), set([u'n_23', u'n_24']), 2, 0),
            ReducibleFeature(5, 1, set([u'n_17', u'n_20', u'n_18', u'n_19']), set([]), 1, 0),
            ReducibleFeature(5, 2, set([u'n_65', u'n_64', u'n_63', u'n_62', u'n_61']), set([u'n_60']), 3, 1),
            ReducibleFeature(5, 2, set([u'n_81', u'n_83', u'n_82', u'n_84']), set([u'n_201', u'n_202']), 3, 3),
            ReducibleFeature(5, 2, set([u'n_52', u'n_53', u'n_51', u'n_54']), set([u'n_202', u'n_203', u'n_204']), 2, 0),
            ReducibleFeature(5, 2, set([u'n_128', u'n_125', u'n_124', u'n_127', u'n_126', u'n_121', u'n_123', u'n_122']), set([u'n_142', u'n_141']), 4, 0),
            ReducibleFeature(5, 1, set([u'n_222', u'n_220', u'n_221']), set([u'n_223']), 1, 0),
            ReducibleFeature(5, 1, set([u'n_240', u'n_241', u'n_242']), set([u'n_243']), 1, 0),
            ReducibleFeature(5, 2, set([u'n_31', u'n_32']), set([u'n_202', u'n_203', u'n_204']), 1, 0),
            ReducibleFeature(5, 2, set([u'n_136', u'n_134', u'n_135', u'n_132', u'n_133', u'n_131']), set([]), 5, 0),
            ReducibleFeature(2, 2, [u'n_243', u'n_223'], [u'n_233'], 0, 0),
            ReducibleFeature(5, 1, set([u'n_23', u'n_24']), set([u'n_201', u'n_202']), 1, 0),
            ReducibleFeature(5, 2, set([u'n_125', u'n_124', u'n_127', u'n_126', u'n_123', u'n_122']), set([u'n_142', u'n_141']), 4, 0),
            ReducibleFeature(5, 2, set([u'n_52', u'n_51']), set([u'n_202', u'n_203', u'n_204']), 1, 0),
            ReducibleFeature(2, 1, [u'n_125', u'n_124'], [u'n_142', u'n_141'], 0, 0),
            ReducibleFeature(6, 1, set([u'n_146', u'n_145', u'n_144', u'n_143', u'n_142', u'n_141']), set([]), 0, 0),
            ReducibleFeature(6, 2, set([u'n_151', u'n_152', u'n_154', u'n_155']), set([u'n_203', u'n_204']), 0, 0),
            ReducibleFeature(4, 1, [u'n_204'], [u'n_201', u'n_202', u'n_203'], 0, 0),
            ReducibleFeature(5, 2, set([u'n_201', u'n_7', u'n_8', u'n_9']), set([u'n_202', u'n_203']), 2, 0),
            ReducibleFeature(5, 2, set([u'n_8', u'n_9']), set([u'n_202', u'n_7', u'n_203']), 1, 0),
            ReducibleFeature(2, 1, [u'n_7'], [u'n_202', u'n_203'], 0, 0),
            ReducibleFeature(7, 1, set([u'n_161', u'n_163', u'n_162', u'n_165', u'n_164', u'n_167', u'n_166', u'n_168']), set([]), 0, 0),
            ReducibleFeature(7, 1, set([u'n_172', u'n_173', u'n_171', u'n_176', u'n_177', u'n_175', u'n_202', u'n_203']), set([]), 0, 0)
        ]
        canon_str_exp = "(0.1;(5.2.3.1;(0,((0,1))),(0,((0,2))),(0,((0,3))),(0,((0,4))),(0,((0,5))),(0,((1,2))),(0,((2,3))),(0,((3,4))),(0,((4,5))),(0,((5,1))),1 (5.2.3.1),2 (5.2.3.1),3 (5.2.3.1),4 (5.2.3.1),5 (5.2.3.1)),0 (5.2.3.1)),(2.2;(0.1;(5.1.1;(n,((0,1))),(n,((0,2))),(n,((0,3))),(n,((1,2))),(n,((1,3))),(n,((2,3))),0,0,0),G),((4.1;((4.3;(n,((0,3))),(n,((3,1))),(n,((3,2))),0),((3,0,1),(3,1,0))),((4.3;(n,((0,3))),(n,((3,1))),(n,((3,2))),0),((3,0,2),(3,2,0))),((4.3;(n,((0,3))),(n,((3,1))),(n,((3,2))),0),((3,1,2),(3,2,1))),G),((0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0))),(0.1;(5.1.1;(n,((0,1))),(n,((0,2))),(n,((0,3))),(n,((1,2))),(n,((1,3))),(n,((2,3))),0,0,0),G),(0.1;(5.1.1;(n,((0,1))),(n,((0,2))),(n,((0,3))),(n,((1,2))),(n,((1,3))),(n,((2,3))),0,0,0),G)),(5.1.1;(0,((0,1))),(0,((0,2))),(0,((0,3))),(0,((1,2))),(0,((1,3))),(0,((2,3))),1 (5.1.1),2 (5.1.1),3 (5.1.1),4 (5.1.1)),(5.2.5;(0,((0,1))),(0,((0,2))),(0,((0,3))),(0,((1,2))),(0,((1,4))),(0,((2,5))),(0,((3,4))),(0,((3,5))),(0,((4,5))),1 (5.2.5),2 (5.2.5),3 (5.2.5),4 (5.2.5),5 (5.2.5),6 (5.2.5)),(6.1;((0.2;((2.1;((5.2.4;((5.2.4;(n,((0,3))),(n,((1,3))),(n,((3,2))),0),((0,1,2),(1,0,2))),(n,((0,1))),(n,((3,0))),(n,((3,1))),0,0),((0,1))),0,(n,((1,0))),0,((5.2.4;((5.2.4;(n,((3,0))),(n,((3,1))),(n,((3,2))),0),((0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0))),(n,((0,1))),(n,((0,3))),(n,((1,3))),0,0),((1,0)))),((0,1))),(0,((1,0)))),((0,1))),(0,((0,2))),(0,((0,3))),(0,((1,4))),(0,((1,5))),(0,((2,4))),(0,((2,5))),(0,((3,4))),(0,((5,3))),1 (6.1),2 (6.1),3 (6.1),4 (6.1),5 (6.1),6 (6.1)),(7.1;((0.2;((2.1;((5.2.1;((3;((4.2;(0,((3,0))),(0,((3,1))),(0,((3,2))),1 (4.2)),((0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0))),((4.2;(0,((3,0))),(0,((3,1))),(0,((3,2))),2 (4.2)),((0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0)))),((0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0))),(0,((0,3))),(0,((1,4))),4 (4.2),5 (4.2)),((1,0,2),(1,2,0))),((5.2.2;((0.2;((0.2;((5.2.3.3;(0,((0,1))),(0,((0,2))),(0,((0,3))),(0,((1,2))),(0,((1,4))),(0,((3,4))),(0,((3,5))),(0,((4,5))),1 (5.2.3.3),2 (5.2.3.3),3 (5.2.3.3),4 (5.2.3.3)),((0,1))),(0,((0,1)))),((0,1))),((5.1.1;((5.1.2;(0,((2,0))),(0,((2,1))),(0,((2,3))),(0,((3,0))),(0,((3,1))),1 (5.1.2),2 (5.1.2)),((0,1),(1,0))),(0,((0,2))),(0,((0,3))),(0,((1,2))),(0,((1,3))),3 (5.1.2),4 (5.1.2)),((0,1),(1,0)))),((3,0))),((4.1;((0.2;((6.2;(0,((0,2))),(0,((2,3))),(0,((3,1))),(0,((4,0))),(0,((4,3))),(0,((5,1))),(0,((5,2))),(0,((5,4))),1 (6.2),2 (6.2),4 (6.2),5 (6.2)),((0,1))),(0,((0,1)))),((0,3))),((3;((3;((4.1;(0,((3,0))),(0,((3,1))),(0,((3,2))),1 (4.1)),((0,1,2),(0,2,1),(1,0,2),(1,2,0),(2,0,1),(2,1,0))),((5.2.1;(0,((0,1))),(0,((0,2))),(0,((0,3))),(0,((1,2))),(0,((1,4))),1 (5.2.1 - 1),2 (5.2.1 - 1)),((0,1,2)))),((0,1,2))),((5.2.1;((5.2.2;(0,((0,3))),(0,((3,1))),(0,((3,2))),3 (5.2.2)),((0,1,2),(0,2,1))),((5.2.2;(0,((0,3))),(0,((3,1))),(0,((3,2))),4 (5.2.2)),((3,1,4),(3,4,1))),(0,((0,1))),(0,((0,3))),(0,((3,1))),1 (5.2.2),2 (5.2.2)),((2,0,1)))),((1,0,3))),(0,((1,3))),(0,((2,3))),base_4),((1,0,3))),(0,((2,3))),(0,((3,1))),base_1),((0,2,1))),3 (4.2)),((0,1))),(0,((0,1)))),((0,1))),(0,((2,0))),(0,((2,3))),(0,((3,1))),(0,((4,0))),(0,((4,5))),(0,((5,1))),(0,((6,2))),(0,((6,4))),(0,((6,7))),(0,((7,3))),(0,((7,5))),1 (7.2),2 (7.2),3 (7.2),5 (7.2),6 (7.2),7 (7.2),base_2,base_3),(7.1;(0,((0,1))),(0,((0,2))),(0,((0,3))),(0,((1,4))),(0,((1,5))),(0,((2,4))),(0,((2,6))),(0,((3,5))),(0,((3,6))),(0,((4,7))),(0,((5,7))),(0,((6,7))),1 (7.1),2 (7.1),3 (7.1),4 (7.1),5 (7.1),6 (7.1),7 (7.1),8 (7.1))"
        tw, canon_str, features = arnborg_proskurowski.run_algorithm(self.graph_tw_3, return_features=True)
        self.common_asserts(tw, 3, canon_str, canon_str_exp, features, features_exp)
        tw_1 = arnborg_proskurowski.get_treewidth(self.graph_tw_3)
        canon_str_1 = arnborg_proskurowski.get_canonical_representation(self.graph_tw_3)
        features_1 = arnborg_proskurowski.get_reduced_features(self.graph_tw_3)
        self.common_asserts(tw_1, 3, canon_str_1, canon_str_exp, features_1, features_exp)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()