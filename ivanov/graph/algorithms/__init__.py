'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from ivanov.graph.algorithms import arnborg_proskurowski
from ivanov.graph.hypergraph import Hypergraph
import networkx as nx
import random
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
def r_ball_hyper(hypergraph, center, r, edge_dir=0, center_default_color=False):
    '''The same as r_ball but for Hypergraph.
    '''
    assert type(hypergraph) is Hypergraph
    
    visited_nodes = set()
    
    def recurse(u, i):
        visited_nodes.add(u)
        edges = hypergraph.edges_iter_dir(u, dir_code=edge_dir)
        skip_edges = set()
        for edge in edges:
            if edge in skip_edges:
                continue
            endpoints = hypergraph.endpoints(edge)
            new_endpoints = set(endpoints) - set([u])
            for v in new_endpoints:
                if not rball.has_node(v):
                    rball.add_node(v, attr_dict=copy.deepcopy(hypergraph.node[v]))
            
            first_new_endpoint = next(iter(new_endpoints))
            # TODO: this condition may be tricky if the graph has hyperedges
            if not rball.has_edge(u, first_new_endpoint, edge_dir):
                parallel_edges = hypergraph.edges_iter_dir(u, first_new_endpoint, dir_code=edge_dir)
                # add all parallel edges in the same direction to the r-ball
                for parallel_edge in parallel_edges:
                    skip_edges.add(parallel_edge)
                    p_edge_attr = hypergraph.edge(parallel_edge)
                    direction = p_edge_attr["direction"]
                    # TODO: not safe if we have hyperedges
                    rball.add_edge(endpoints, direction=copy.deepcopy(direction), label=u",".join(copy.deepcopy(p_edge_attr["labels"])))
            
            if i < r:
                for v in new_endpoints:
                    if v not in visited_nodes:
                        recurse(v, i + 1)
    
    rball = Hypergraph()
    if center_default_color:
        # the center node's default color is 0 ("owl:Thing")
        rball.add_node(center, attr_dict={"labels": ["0"]})
    else:
        rball.add_node(center, attr_dict=copy.deepcopy(hypergraph.node[center]))
    if r > 0:
        recurse(center, 1)
    
    rball.init_parallel_edges_groups()
    rball.init_nodes_with_n_neighbors()
    
    return rball

def isomorphic(graph1, graph2):
    '''Isomorphism test based on Arnborg & Proskurowski. Works only for
    graphs with tree-width <= 3. If the tree-width is >3 returns False.
    '''
    g1_tw, g1_canon_str = arnborg_proskurowski.run_algorithm(graph1)
    g2_tw, g2_canon_str = arnborg_proskurowski.run_algorithm(graph2)
    if g1_tw != -1 and g1_tw == g2_tw and g1_canon_str == g2_canon_str:
        return True
    return False

def drop_edges_by_probability(graph, probability):
    new_graph = graph.copy()
    edges_to_remove = []
    for edge in new_graph.edges_iter():
        r = random.uniform(0, 1)
        if r <= probability:
            edges_to_remove.append(edge)
    
    new_graph.remove_edges_from(edges_to_remove)
    return new_graph
