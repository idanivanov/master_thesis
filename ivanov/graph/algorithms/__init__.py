'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.hypergraph import Hypergraph
import networkx as nx
import copy

def r_ball(graph, center, r, edge_dir=0):
    '''Extract an r-ball around a node in a graph as a subgraph.
    :param graph: Networkx graph
    :param center: the center node of the r-ball
    :param r: radius of the r-ball (in hops)
    :param edge_dir: the direction of edges to be considered (0 - all edges, 1 - only outgoing, -1 - only incoming)
    :return: r-ball as a Networkx graph
    '''
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

# TODO: can be optimized
def r_ball_hyper(hypergraph, center, r, edge_dir=0):
    '''The same as r_ball but for Hypergraph.
    '''
    assert type(hypergraph) is Hypergraph
    
    visited_nodes = set()
    
    def recurse(u, i):
        visited_nodes.add(u)
        edges = hypergraph.edges_iter(u)
        for edge in edges:
            endpoints = hypergraph.endpoints(edge)
            new_endpoints = set(endpoints) - set([u])
            if any(map(lambda node: node in visited_nodes, new_endpoints)):
                continue
            edge_attr = hypergraph.edge(edge)
            direction = edge_attr["direction"]
            if edge_dir < 0 and any(map(lambda dir_perm: dir_perm.index(u) > 0, direction)) or \
               edge_dir > 0 and any(map(lambda dir_perm: dir_perm.index(u) < len(dir_perm) - 1, direction)) or \
               edge_dir == 0:
                for v in new_endpoints:
                    rball.add_node(v, attr_dict=copy.deepcopy(hypergraph.node[v]))
                rball.add_edge(endpoints, direction=copy.deepcopy(direction), label=u",".join(copy.deepcopy(edge_attr["labels"])))
                if i < r:
                    for v in new_endpoints:
                        recurse(v, i + 1)
    
    rball = Hypergraph()
    rball.add_node(center, attr_dict=copy.deepcopy(hypergraph.node[center]))
    if r > 0:
        recurse(center, 1)
    
    rball.init_parallel_edges_groups()
    rball.init_nodes_with_n_neighbors()
    
    return rball
