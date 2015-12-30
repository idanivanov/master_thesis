'''
Created on Dec 30, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms import arnborg_proskurowski

def extract_shingles(feature):
    '''Extracts (naively) all shingles contained in a feature.
    :param feature: A Networkx graph.
    :return A generator of shingles.
    '''
    def get_all_colorings(nodes_colors):
        def process_node(nodes, i):
            if i < len(nodes):
                for color in nodes_colors[nodes[i]]:
                    for color_selection in process_node(nodes, i + 1):
                        yield [color] + color_selection
            elif i == len(nodes):
                yield []
        return process_node(list(nodes_colors), 0)
    
    def create_shingle(coloring):
        shingle_graph = feature.copy()
        i = 0
        for node in feature.nodes_iter():
            shingle_graph.node[node]["labels"] = [coloring[i]]
            i += 1
        _, shingle = arnborg_proskurowski.get_canonical_representation(shingle_graph)
        return shingle
    
    nodes_colors = {node: feature.node[node]["labels"] for node in feature.nodes_iter()}
    colorings = get_all_colorings(nodes_colors)
    for coloring in colorings:
        yield create_shingle(coloring)
