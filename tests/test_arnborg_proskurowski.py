'''
Created on Dec 28, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.arnborg_proskurowski.reducible_feature import ReducibleFeature
from ivanov.graph.algorithms import arnborg_proskurowski
from tests import example_graphs
import unittest

class TestArnborgProskurowski(unittest.TestCase):
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
        tw, canon_str, features = arnborg_proskurowski.run_algorithm(example_graphs.ap_graph_tw_2, return_features=True)
        self.common_asserts(tw, 2, canon_str, canon_str_exp, features, features_exp)
        tw_1 = arnborg_proskurowski.get_treewidth(example_graphs.ap_graph_tw_2)
        canon_str_1 = arnborg_proskurowski.get_canonical_representation(example_graphs.ap_graph_tw_2)
        features_1 = arnborg_proskurowski.get_reduced_features(example_graphs.ap_graph_tw_2)
        self.common_asserts(tw_1, 2, canon_str_1, canon_str_exp, features_1, features_exp)
     
    def testTW_2_ring(self):
        features_exp = [
            ReducibleFeature(2, 2, ["n_1"], ["n_2", "n_3", "n_4", "n_5"]),
        ]
        canon_str_exp = "(2.2;1,(a,((0,1))),2,(b,((0,1))),3,(c,((0,1))),4,(d,((0,1))),5,(e,((0,1))))"
        tw, canon_str, features = arnborg_proskurowski.run_algorithm(example_graphs.ap_ring_graph, return_features=True)
        self.common_asserts(tw, 2, canon_str, canon_str_exp, features, features_exp)
        tw_1 = arnborg_proskurowski.get_treewidth(example_graphs.ap_ring_graph)
        canon_str_1 = arnborg_proskurowski.get_canonical_representation(example_graphs.ap_ring_graph)
        features_1 = arnborg_proskurowski.get_reduced_features(example_graphs.ap_ring_graph)
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
        tw, canon_str, features = arnborg_proskurowski.run_algorithm(example_graphs.ap_graph_tw_3, return_features=True)
        self.common_asserts(tw, 3, canon_str, canon_str_exp, features, features_exp)
        tw_1 = arnborg_proskurowski.get_treewidth(example_graphs.ap_graph_tw_3)
        canon_str_1 = arnborg_proskurowski.get_canonical_representation(example_graphs.ap_graph_tw_3)
        features_1 = arnborg_proskurowski.get_reduced_features(example_graphs.ap_graph_tw_3)
        self.common_asserts(tw_1, 3, canon_str_1, canon_str_exp, features_1, features_exp)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()