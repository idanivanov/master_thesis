'''
Created on Jan 13, 2016

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_nodes_mining.sketch_matrix import SketchMatrix
from ivanov.graph.algorithms import similar_nodes_mining
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import rdf
import helpers
import time
from ivanov.graph.algorithms.similar_nodes_mining.characteristic_matrix import CharacteristicMatrix

if __name__ == '__main__':
    dataset = "dummy"
    r_in = 3
    r_out = 2
    r_all = 0
    wl_iterations = 4
    k = 10
    L = 9
    
    in_files = helpers.datasets[dataset]["files"]
    
    start = time.time()
    graph, node_id_map = rdf.convert_rdf_to_nx_graph(in_files, discard_classes=False)
    print "Converting RDF to NetworkX graph took", time.time() - start, "s"
    
    start = time.time()
    hypergraph = Hypergraph(graph)
    print "Building hypergraph took", time.time() - start, "s"
    
    start = time.time()
    hypergraph.save_to_file("../output_2/{0}_hgraph".format(dataset))
    print "Saving hypergraph took", time.time() - start, "s"
    
#     start = time.time()
#     hypergraph = Hypergraph.load_from_file("../output_2/{0}_hgraph".format(dataset))
#     print "Reading hypergraph took", time.time() - start, "s"
    
    print "Building characteristic matrix may take", CharacteristicMatrix.estimate_time_to_build(hypergraph.number_of_nodes()), "s"
    start = time.time()
    ch_matrix = CharacteristicMatrix(hypergraph, r_in=r_in, r_out=r_out, r_all=r_all, wl_iterations=wl_iterations)
    print "Building characteristic matrix took", time.time() - start, "s"
    
    start = time.time()
    ch_matrix.save_to_file("../output_2/{0}_ch_matrix".format(dataset))
    print "Saving characteristic matrix took", time.time() - start, "s"
    
    print "Building sketch matrix may take", SketchMatrix.estimate_time_to_build(hypergraph.number_of_nodes()), "s"
    start = time.time()
    sketch_matrix = SketchMatrix(k, L, ch_matrix)
    print "Building sketch matrix took", time.time() - start, "s"
     
    start = time.time()
    sketch_matrix.save_to_file("../output_2/{0}_sketch".format(dataset))
    print "Saving sketch matrix took", time.time() - start, "s"
    
    start = time.time()
    sim_mat, cols_nodes_map = similar_nodes_mining.get_node_similarity_matrix(sketch_matrix)
    print "Building simiarity matrix took", time.time() - start, "s"
     
    start = time.time()
    similar_nodes = similar_nodes_mining.get_similar_nodes(sim_mat, cols_nodes_map)
    print "Extracting similar nodes took", time.time() - start, "s"
     
    print similar_nodes