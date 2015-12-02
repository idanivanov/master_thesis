'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms import arnborg_proskurowski
from ivanov.graph.hypergraph import Hypergraph
from ivanov.statistics import treewidth
from ivanov.graph import nxext
from ivanov.graph import algorithms
from ivanov import graph
from ivanov.graph import rdf
import codecs

def compute_rballs_tw(in_files, output_dir):
    nx_graph = rdf.convert_rdf_to_nx_graph(in_files)
    nodes_in_graph = nx_graph.number_of_nodes()
    print "Nodes in graph:", nodes_in_graph
    
    for d in ["in", "out", "all"]:
        rballs_with_big_tw = set()
        for r in [2, 3, 4, 5]:
            out_file = codecs.open(output_dir + "tw_r{0}_{1}".format(r, d), "w", "utf8")
             
            i = 0
            for node in nx_graph.nodes_iter():
                print "-------------------------------------"
                print "Node {0}/{1} ({2})".format(i, nodes_in_graph, node)
                print "r = {0}, d = {1}".format(r, d)
                if node in rballs_with_big_tw:
                    # don't compute treewidth for r-balls which are known to be big
                    ap_result = (-1, u"")
                else:
                    rball = algorithms.r_ball(nx_graph, node, r, -1 if d == "in" else 1 if d == "out" else 0)
                    print "r-ball nodes:", rball.number_of_nodes()
                    ap_result = arnborg_proskurowski.get_canonical_representation(rball, False)
                    if ap_result[0] == -1:
                        rballs_with_big_tw.add(node)
                print "Treewidth: ", ap_result[0]
                line = u"{0},{1}\n".format(nx_graph.node[node]["labels"][0].replace(u",", u"[comma]"), ap_result[0])
                out_file.write(line)
#                 nxext.visualize_graph(rball, node_labels=True, edge_labels=False)
                i += 1
             
            out_file.close()

def aggregate_results(path_to_files, percent=False):
    out_file = codecs.open(path_to_files + "agg{0}".format("_percent" if percent else ""), "w", "utf8")
    
    out_file.write(",".join(["params", "0", "1", "2", "3", ">=4"] + ([] if percent else ["total"])) + "\n")
    
    for d in ["in", "out", "all"]:
        for r in [2, 3, 4, 5]:
            agg = treewidth.aggregate(path_to_files + "tw_r{0}_{1}".format(r, d))
            out_file.write("[{0};{1}]".format(r, d))
            for tw in ["0", "1", "2", "3", "-1"]:
                if agg.has_key(tw):
                    if percent:
                        value = (100. / float(agg["total"])) * float(agg[tw])
                    else:
                        value = agg[tw]
                    out_file.write(",{0}".format(value))
                else:
                    out_file.write(",0")
            if not percent:
                out_file.write(",{0}".format(agg["total"]))
            out_file.write("\n")
    
    out_file.close()

def test_graph(path_to_graph_file):
    nx_graph = graph.load_graph(path_to_graph_file)
    return arnborg_proskurowski.get_canonical_representation(nx_graph)

if __name__ == '__main__':
    path = "../data/"
    in_files = [
        path + "family.rdf.owl.rdf"
    ]
    
    compute_rballs_tw(in_files, "../output/fam/")
#     aggregate_results("../output/fam/")
#     aggregate_results("../output/fam/", True)
#     print test_graph("../output/peel/small_graph")
