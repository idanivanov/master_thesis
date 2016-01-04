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
    
    prime = 18446744073709551629 # the first prime after 2^64
    r = 18446744073709551616 # 2^64
    hash_functions_params = [{'a': 6622654284345900829L, 'b': 13490758124686681528L}, {'a': 14663894821143669455L, 'b': 6439844538002334591L}, {'a': 2379686874529457104L, 'b': 8185526651052600452L}, {'a': 12967927669330969122L, 'b': 12462161476562369326L}, {'a': 12794731006915055423L, 'b': 17552924732285677865L}, {'a': 1249276043662745793L, 'b': 7989670371758500388L}, {'a': 3064986392191475918L, 'b': 12349349783191557321L}, {'a': 2534473384334947021L, 'b': 5005824705426043577L}, {'a': 16912154622565403339L, 'b': 11683889585300241627L}, {'a': 1032581858635566387L, 'b': 10914269360685178764L}, {'a': 7471181510043765781L, 'b': 3279860973155612242L}, {'a': 17704488587427593373L, 'b': 16922471305847151249L}, {'a': 16792499234352382717L, 'b': 8700104495548587505L}, {'a': 4121026640435954145L, 'b': 3276327854692116029L}, {'a': 13888905599880235513L, 'b': 17481908733172052590L}, {'a': 12431254451553104855L, 'b': 5396870450091507175L}, {'a': 11385350211508996660L, 'b': 13559896054040943139L}, {'a': 14291473694146928306L, 'b': 7925294647560394093L}, {'a': 16513833748719184739L, 'b': 16099270172953105824L}, {'a': 11779416465886848533L, 'b': 15892616741254912007L}, {'a': 9240496208648513444L, 'b': 6981722690177561747L}, {'a': 12007471701826633683L, 'b': 7845957561360406036L}, {'a': 6212354011279394331L, 'b': 7786277521262883394L}, {'a': 8295114476383850412L, 'b': 3559574395980189864L}, {'a': 2840760103249698135L, 'b': 9039618503394705653L}, {'a': 11651848732269887495L, 'b': 14155330126232758258L}, {'a': 671576611119487343L, 'b': 6809657065378728388L}, {'a': 5214669165097706911L, 'b': 13046091877741266060L}, {'a': 4660090283705429971L, 'b': 17957746711749393063L}, {'a': 1049162976580565274L, 'b': 6140551455473248011L}, {'a': 7482135423674526325L, 'b': 9194859688198993067L}, {'a': 13883736500202622856L, 'b': 5432785255208381181L}, {'a': 2848206983405151376L, 'b': 3128726294201453056L}, {'a': 13346288123623923462L, 'b': 1172444666856150047L}, {'a': 2068157107344484837L, 'b': 8837963890391637193L}, {'a': 3382042223439732776L, 'b': 14794475172608721540L}, {'a': 9597465411076234193L, 'b': 3151761442720711649L}, {'a': 7997750766485303390L, 'b': 18443268212523993880L}, {'a': 7770065253488600912L, 'b': 10185239109738382629L}, {'a': 10311731632837870741L, 'b': 5352534570416784667L}, {'a': 1164108093774745427L, 'b': 605703292256291067L}, {'a': 17040849459953732327L, 'b': 6785271306060613007L}, {'a': 7742261007483192367L, 'b': 2646325709199691789L}, {'a': 448296455842606116L, 'b': 2822233556942286455L}, {'a': 6191613261298296233L, 'b': 16342220155807948960L}, {'a': 5871823293443006412L, 'b': 5954396548803136769L}, {'a': 14960211008779721960L, 'b': 12592416079387816515L}, {'a': 13352384366934960493L, 'b': 1745188683947547383L}, {'a': 16602913703865557199L, 'b': 16108396874341914922L}, {'a': 9620534905295602298L, 'b': 18369294194323128234L}, {'a': 1287637342528393500L, 'b': 12827978415093390676L}, {'a': 9114397444229439552L, 'b': 9403770122483092129L}, {'a': 9611231489494208541L, 'b': 7627469642953105607L}, {'a': 15862715741516605709L, 'b': 7734968008632188725L}, {'a': 834180253894336886L, 'b': 3799041413703722508L}, {'a': 10526978419945216688L, 'b': 13937598156615740310L}, {'a': 18023189281969877572L, 'b': 10366020058609364989L}, {'a': 13966089523344954638L, 'b': 11316726372784188152L}, {'a': 1384861904697137947L, 'b': 411456202520680799L}, {'a': 4093127543548598817L, 'b': 12068544110729519712L}, {'a': 2756469592849248694L, 'b': 14271801654450646861L}, {'a': 2834593866484313228L, 'b': 2084470453066858666L}, {'a': 893478113626788010L, 'b': 12970886830418168793L}, {'a': 1339450879162907157L, 'b': 6268511448868851355L}, {'a': 16538002375335366520L, 'b': 12568511068628075163L}, {'a': 10511687532651067309L, 'b': 9655315220608698674L}, {'a': 4154183833167041810L, 'b': 5383963829236263397L}, {'a': 9334276538818312670L, 'b': 9712950934153078946L}, {'a': 8120096958887667937L, 'b': 2621799425318593603L}, {'a': 8304116499567267228L, 'b': 6300621556521452898L}, {'a': 11682782215196859325L, 'b': 14293469317543233268L}, {'a': 10348310926526840553L, 'b': 1012328342892535525L}, {'a': 15411992948023495079L, 'b': 11411735505028828491L}, {'a': 4997812715192147524L, 'b': 933976646724915365L}, {'a': 10298423829827254445L, 'b': 11513327761996235569L}, {'a': 856300551428842283L, 'b': 4428234123680546151L}, {'a': 11357425714271840220L, 'b': 14832625362078748701L}, {'a': 6004758452651174851L, 'b': 2474051783966305155L}, {'a': 3265396422987076051L, 'b': 59276518954600404L}, {'a': 5408732451131803694L, 'b': 14753260736280776201L}, {'a': 825540497978022088L, 'b': 1196539705150643228L}, {'a': 9439969196955910846L, 'b': 9417220117922132275L}, {'a': 2422104852532977473L, 'b': 8414687526783308171L}, {'a': 545322038667845555L, 'b': 11898847332041986249L}, {'a': 11025979740179287262L, 'b': 10505589197139132062L}, {'a': 16871410842296750357L, 'b': 8219125205865982447L}, {'a': 5799651956469692590L, 'b': 708348538682917038L}, {'a': 2521750435896001113L, 'b': 12690525723436311607L}, {'a': 1605366560863486674L, 'b': 13989431613919596840L}, {'a': 8145425794857216702L, 'b': 7067553155675677523L}, {'a': 5534971901534316448L, 'b': 1164394490268677554L}, {'a': 14171088325502590452L, 'b': 4264717265267276667L}, {'a': 17729599392032185126L, 'b': 14992343286457683060L}, {'a': 8051625486829802332L, 'b': 16007177203911090885L}, {'a': 16067211209864300895L, 'b': 14544459867370609037L}, {'a': 12684807960814431295L, 'b': 2900389010917787158L}, {'a': 12969981693232356250L, 'b': 14059735551500002878L}, {'a': 3243591966821753809L, 'b': 1201495600004953737L}, {'a': 17059071007303085106L, 'b': 7519280169100496728L}, {'a': 8251033868083505383L, 'b': 5573906535909754585L}]
    
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
        h = SketchMatrix.hash_func_generator(a, b, self.r, self.prime)
        
        fp_exp = 13099543911338852352
        fp = fingerprint.get_minhash_fingerprint_naive(self.dummy_feature, h)
        self.assertEqual(fp_exp, fp, "The minhash fingerprint extracted from the feature is not correct.")

#     def testSketchMatrix(self):
#         def build_hash_functions(params_dict):
#             hash_functions = []
#             for params in params_dict:
#                 h = func_generator(params['a'], params['b'], self.r, self.prime)
#                 hash_functions.append(h)
#             return hash_functions
#         hash_functions = build_hash_functions(self.hash_functions_params)
#         dummy_hypergraph = Hypergraph(self.dummy_graph)
#         sketch = SketchMatrix(10, 10, dummy_hypergraph, r_in=1, r_out=1, r_all=0, wl_iterations=4, hash_functions=hash_functions)
#         print sketch # TODO: compare with expected sketch

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testFeatureExtraction']
    unittest.main()