'''
Created on Jan 13, 2016

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms.similar_graphs_mining.characteristic_matrix import CharacteristicMatrix
from ivanov.graph.algorithms.similar_graphs_mining.sketch_matrix import SketchMatrix
from ivanov.graph.algorithms import similar_nodes_mining
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import rdf
from ivanov import inout
import helpers
import time

dataset = "famont-ext"
r_in = 3
r_out = 2
r_all = 0
wl_iterations = 4
k = 10
L = 9

time_format = "%H:%M:%S, %d.%m.%Y"

path = "../output_2/famont_test/"

def calculate_ch_matrix():
    in_files = helpers.datasets[dataset]["files"]
    
    print "Converting RDF to NetworkX graph started at", time.strftime(time_format)
    start = time.time()
    graph, node_id_map = rdf.convert_rdf_to_nx_graph(in_files, discard_classes=False)
    print "Converting RDF to NetworkX graph took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Saving NodeID map started at", time.strftime(time_format)
    start = time.time()
    inout.save_to_file(node_id_map, path + "{0}_node_id_map".format(dataset))
    print "Saving NodeID map took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Building hypergraph started at", time.strftime(time_format)
    start = time.time()
    hypergraph = Hypergraph(graph)
    print "Building hypergraph took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Saving hypergraph started at", time.strftime(time_format)
    start = time.time()
    hypergraph.save_to_file(path + "{0}_hgraph".format(dataset))
    print "Saving hypergraph took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Building characteristic matrix started at", time.strftime(time_format)
    start = time.time()
    rballs_database, index_node_map = similar_nodes_mining.extract_rballs_database(hypergraph, r_in=r_in, r_out=r_out, r_all=r_all)
    ch_matrix = CharacteristicMatrix(rballs_database, hypergraph.number_of_nodes(), wl_iterations=wl_iterations)
    print "Building characteristic matrix took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Saving Column index to Node map started at", time.strftime(time_format)
    start = time.time()
    inout.save_to_file(index_node_map, path + "{0}_index_node_map".format(dataset))
    print "Saving Column index to Node map took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Saving characteristic matrix started at", time.strftime(time_format)
    start = time.time()
    ch_matrix.save_to_file(path + "{0}_ch_matrix".format(dataset))
    print "Saving characteristic matrix took", time.time() - start, "s"
    print "-----------------------------------------"
    
    return ch_matrix, hypergraph, index_node_map, node_id_map

def load_ch_matrix():
    print "Reading NodeID map started at", time.strftime(time_format)
    start = time.time()
    node_id_map = inout.load_from_file(path + "{0}_node_id_map".format(dataset))
    print "Reading NodeID map took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Reading hypergraph started at", time.strftime(time_format)
    start = time.time()
    hypergraph = Hypergraph.load_from_file(path + "{0}_hgraph".format(dataset))
    print "Reading hypergraph took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Reading characteristic matrix started at", time.strftime(time_format)
    start = time.time()
    ch_matrix = CharacteristicMatrix.load_from_file(path + "{0}_ch_matrix".format(dataset))
    print "Reading characteristic matrix took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Reading Column index to Node map started at", time.strftime(time_format)
    start = time.time()
    index_node_map = inout.load_from_file(path + "{0}_index_node_map".format(dataset))
    print "Reading Column index to Node map took", time.time() - start, "s"
    print "-----------------------------------------"
    
    return ch_matrix, hypergraph, index_node_map, node_id_map

def calculate_sketch_matrix(ch_matrix, hypergraph):
    print "Building sketch matrix started at", time.strftime(time_format)
    start = time.time()
    sketch_matrix = SketchMatrix(k, L, ch_matrix)
    print "Building sketch matrix took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Saving sketch matrix started at", time.strftime(time_format)
    start = time.time()
    sketch_matrix.save_to_file(path + "{0}_sketch".format(dataset))
    print "Saving sketch matrix took", time.time() - start, "s"
    print "-----------------------------------------"
    
    return sketch_matrix

def load_sketch_matrix():
    print "Reading NodeID map started at", time.strftime(time_format)
    start = time.time()
    node_id_map = inout.load_from_file(path + "{0}_node_id_map".format(dataset))
    print "Reading NodeID map took", time.time() - start, "s"
    
    print "Reading sketch matrix started at", time.strftime(time_format)
    start = time.time()
    sketch_matrix = SketchMatrix.load_from_file(path + "{0}_sketch".format(dataset))
    print "Reading sketch matrix took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Reading Column index to Node map started at", time.strftime(time_format)
    start = time.time()
    index_node_map = inout.load_from_file(path + "{0}_index_node_map".format(dataset))
    print "Reading Column index to Node map took", time.time() - start, "s"
    print "-----------------------------------------"
    
    return sketch_matrix, index_node_map, node_id_map

if __name__ == '__main__':
    ch_matrix, hypergraph, index_node_map, node_id_map = calculate_ch_matrix()
#     ch_matrix, hypergraph, index_node_map, node_id_map = load_ch_matrix()
    
    sketch_matrix = calculate_sketch_matrix(ch_matrix, hypergraph)
#     sketch_matrix, index_node_map, node_id_map = load_sketch_matrix()
    
    print "Building similarity matrix started at", time.strftime(time_format)
    start = time.time()
    sim_mat = similar_nodes_mining.get_node_similarity_matrix(sketch_matrix)
    print "Building similarity matrix took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Extracting similar nodes started at", time.strftime(time_format)
    start = time.time()
    similar_nodes = similar_nodes_mining.get_all_similar_nodes(sim_mat, index_node_map)
    print "Extracting similar nodes took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "Saving similar nodes started at", time.strftime(time_format)
    start = time.time()
    inout.save_to_file(similar_nodes, path + "{0}_similar_nodes".format(dataset))
    print "Saving similar nodes took", time.time() - start, "s"
    print "-----------------------------------------"
    
    print "DONE!"
