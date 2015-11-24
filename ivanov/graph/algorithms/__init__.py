'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

import networkx as nx
import copy

'''
Extract an r-ball around a node in a graph as a subgraph.

@param graph: networkx graph
@param center: the center node of the r-ball
@param r: radius of the r-ball (in hops)
@param edge_dir: the direction of edges to be considered (0 - all edges, 1 - only outgoing, -1 - only incoming)

@return: r-ball as a networkx graph
'''
def r_ball(graph, center, r, edge_dir=0):
    def recurse(u, i):
        if edge_dir <= 0:
            predecessors = graph.predecessors_iter(u)
            for v in predecessors:
                rball.add_node(v, attr_dict=copy.deepcopy(graph.node[v]))
                edges = graph.edge[v][u]
                for e in edges:
                    rball.add_edge(v, u, attr_dict=copy.deepcopy(edges[e]))
                if i < r:
                    recurse(v, i + 1)
        if edge_dir >= 0:
            successors = graph.successors_iter(u)
            for v in successors:
                rball.add_node(v, attr_dict=copy.deepcopy(graph.node[v]))
                edges = graph.edge[u][v]
                for e in edges:
                    rball.add_edge(u, v, attr_dict=copy.deepcopy(edges[e]))
                if i < r:
                    recurse(v, i + 1)
    
    rball = nx.MultiDiGraph()
    rball.add_node(center, attr_dict=copy.deepcopy(graph.node[center]))
    if r > 0:
        recurse(center, 1)
    
    return rball
