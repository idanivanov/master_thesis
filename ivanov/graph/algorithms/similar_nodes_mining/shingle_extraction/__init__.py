'''
Created on Dec 30, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms import arnborg_proskurowski
from ivanov.graph import nxext
import networkx as nx

def extract_shingles(feature):
    '''Extracts (naively) all shingles contained in a feature (a shingle is created for each
    possible way to remove multiple colors per node and parallel edges).
    :param feature: A Networkx graph.
    :return A generator of shingles.
    '''
    def estimate_number_of_shingles(parallel_edge_free_features_count, nodes_colors):
        colors = [len(nodes_colors[node]) for node in nodes_colors]
        return parallel_edge_free_features_count * reduce(lambda x, y: x * y, colors)
    
    def get_all_parallel_edge_free_groupings():
        '''Finds all groups of parallel edges and returns all possible graphs
        where only one edge per group of parallel edges remains.
        '''
        def process_parallel_edgess(all_adj_nodes, i, new_feature):
            '''Process parallel edges between nodes u and v recursively
            through all adjacent pairs of nodes.
            '''
            u, v = all_adj_nodes[i]
            edges = nxext.get_edge_labels_and_dirs(feature, u, v)
            edges_count = len(edges)
            for j, edge in enumerate(edges):
                if edges_count > 1 and j < edges_count - 1:
                    _new_feature = new_feature.copy()
                else:
                    # no need to copy when the graph will not be used for other iterations
                    _new_feature = new_feature
                
                if edge[1] <= 0:
                    _new_feature.add_edge(v, u, label=edge[0])
                if edge[1] >= 0:
                    _new_feature.add_edge(u, v, label=edge[0])
                
                if i < len(all_adj_nodes) - 1:
                    for processed_feature in process_parallel_edgess(all_adj_nodes, i + 1, _new_feature): 
                        yield processed_feature
                else:
                    yield _new_feature
        
        all_adj_nodes = list(nxext.get_all_adjacent_nodes(feature))
        new_feature = nx.MultiDiGraph()
        new_feature.add_nodes_from(feature.nodes_iter(data=True))
        return process_parallel_edgess(all_adj_nodes, 0, new_feature)
    
    def get_all_colorings(nodes_colors):
        '''Get all possible combinations of the feature graph in which
        each node has exactly one color (label).
        '''
        def process_node(nodes, i):
            if i < len(nodes):
                for color in nodes_colors[nodes[i]]:
                    for color_selection in process_node(nodes, i + 1):
                        yield [color] + color_selection
            elif i == len(nodes):
                yield []
        return process_node(list(nodes_colors), 0)
    
    def create_shingle(parallel_edge_free_feature, coloring):
        shingle_graph = parallel_edge_free_feature.copy()
        i = 0
        for node in shingle_graph.nodes_iter():
            shingle_graph.node[node]["labels"] = [coloring[i]]
            i += 1
        # TODO: this shingle representation has very high collision probability in the Rabin's fingerprint
        shingle = arnborg_proskurowski.get_canonical_representation(shingle_graph)
        return shingle
    
    nodes_colors = {node: feature.node[node]["labels"] for node in feature.nodes_iter()}
    colorings = get_all_colorings(nodes_colors)
    parallel_edge_free_features = list(get_all_parallel_edge_free_groupings())
    shingles_count = estimate_number_of_shingles(len(parallel_edge_free_features), nodes_colors)
    if shingles_count > 100:
        print "Warning: Large number of shingles ({0}) in feature!".format(shingles_count)

    for coloring in colorings:
        for parallel_edge_free_feature in parallel_edge_free_features:
            yield create_shingle(parallel_edge_free_feature, coloring)
