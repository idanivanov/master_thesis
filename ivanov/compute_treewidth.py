'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms import arnborg_proskurowski
from ivanov.graph.hypergraph import Hypergraph
from ivanov.statistics import treewidth
from ivanov.graph import nxext
from ivanov.graph import algorithms
from ivanov import graph, helpers
from ivanov.graph import rdf
import codecs

def compute_rballs_tw(in_files, output_dir):
    nx_graph, uri_node_map = rdf.convert_rdf_to_nx_graph(in_files, discard_classes=True)
    node_uri_map = {node: uri.replace(u",", u"[comma]").replace(u"\n", u"[new_line]") for uri, node in uri_node_map.items()}
    nodes_in_graph = nx_graph.number_of_nodes()
    print "Nodes in graph:", nodes_in_graph
    
    for d in ["in", "out", "all"]:
        rballs_with_big_tw = set()
        for r in [2, 3, 4, 5]:
            out_file = codecs.open(output_dir + "tw_r{0}_{1}".format(r, d), "w", "utf8")
            
            i = 0
            for node in nx_graph.nodes_iter():
                print "-------------------------------------"
                print u"Node {0}/{1} ({2})".format(i, nodes_in_graph, node_uri_map[node])
                print "r = {0}, d = {1}".format(r, d)
                if node in rballs_with_big_tw:
                    # don't compute treewidth for r-balls which are known to be big
                    tw = -1
                else:
                    rball = algorithms.r_ball(nx_graph, node, r, -1 if d == "in" else 1 if d == "out" else 0)
                    print "r-ball nodes:", rball.number_of_nodes()
                    tw = arnborg_proskurowski.get_treewidth(rball)
                    if tw == -1:
                        rballs_with_big_tw.add(node)
                print "Treewidth: ", tw
                line = u"{0},{1}\n".format(node_uri_map[node], tw)
                out_file.write(line)
#                 nxext.visualize_graph(rball, node_labels=True, edge_labels=False)
                i += 1
             
            out_file.close()

def aggregate_results(path_to_files, percent=False, latex=False):
    out_file = codecs.open(path_to_files + "agg{0}".format("_percent" if percent else ""), "w", "utf8")
    
    if not latex:
        out_file.write(",".join(["params", "0", "1", "2", "3", ">=4"] + ([] if percent else ["total"])) + "\n")
    
    for d in ["in", "out", "all"]:
        for r in [2, 3, 4, 5]:
#             if d == "all" and r > 2:
#                 continue
            agg = treewidth.aggregate(path_to_files + "tw_r{0}_{1}".format(r, d))
            if latex:
                out_file.write("$r={0}, e=$ {1}".format(r, d))
            else:
                out_file.write("[{0};{1}]".format(r, d))
            for tw in ["0", "1", "2", "3", "-1"]:
                if agg.has_key(tw):
                    if percent:
                        raw_value = (100. / float(agg["total"])) * float(agg[tw])
                        if latex:
                            value = str(round(raw_value, 2)) + "\%"
                        else:
                            value = raw_value
                    else:
                        value = agg[tw]
                    if latex:
                        out_file.write(" & {0}".format(value))
                    else:
                        out_file.write(",{0}".format(value))
                else:
                    if latex:
                        out_file.write(" & 0\%")
                    else:
                        out_file.write(",0")
            if not percent:
                if latex:
                    out_file.write(" & {0}".format(agg["total"]))
                else:
                    out_file.write(",{0}".format(agg["total"]))
            if latex:
                out_file.write("\\\\\n")
            else:
                out_file.write("\n")
    
    out_file.close()

def test_graph(path_to_graph_file):
    nx_graph = graph.load_graph(path_to_graph_file)
    return arnborg_proskurowski.get_treewidth(nx_graph)

if __name__ == '__main__':
    compute_rballs_tw(helpers.datasets["famont"]["files"], "../output/fam_test/")
#     aggregate_results("../output/fam_test/")
#     aggregate_results("../output/fam_test/", percent=True, latex=True)
#     print test_graph("../output/peel/small_graph")
