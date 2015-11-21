'''
Created on Oct 29, 2015

@author: Ivan Ivanov

Represents a hypergraph with hyperedges of order at most 3.
'''

from networkx.algorithms import bipartite
from itertools import permutations
from ivanov.graph import nxext
from timeit import itertools
import networkx as nx

class Hypergraph(object):
        
    @staticmethod
    def hedge_to_string(hypergraph, hedge_id, permutation):
        assert hedge_id.startswith(u"he_")
        return Hypergraph.edge_to_string(hypergraph, hedge_id, permutation)
    
    @staticmethod
    def edge_to_string(hypergraph, edge_id, permutation):
        '''
        This method implements the procedure for labeling of edges described in section 4.1
        '''
        assert edge_id.startswith(u"he_") or edge_id.startswith(u"e_")
        
        edge_attr = hypergraph.edge(edge_id)
        dir_encodings = []
        for dir_perm in edge_attr["direction"]:
            dir_encoding = map(lambda node: permutation.index(node), dir_perm)
            dir_encodings.append(u"({0})".format(u",".join(unicode(enc) for enc in dir_encoding)))
        hedge_label = edge_attr["labels"][0]
        hedge_dir_str = u"({0})".format(u",".join(sorted(dir_encodings)))
        return u"({0},{1})".format(hedge_label, hedge_dir_str)
    
    def number_of_nodes(self):
        _, nodes = bipartite.sets(self.bipartite_graph)
        return len(nodes)
    
    def number_of_edges(self):
        edges, _ = bipartite.sets(self.bipartite_graph)
        return len(edges)
    
    def number_of_hedges(self):
        edges, _ = bipartite.sets(self.bipartite_graph)
        hedges = filter(lambda edge_id: edge_id.startwith(u"he_"), edges)
        return len(hedges)
    
    def nodes_iter(self):
        return filter(lambda node: self.bipartite_graph.node[node]["bipartite"] == 0, self.bipartite_graph.nodes_iter())
        
    def nodes(self):
        return list(self.nodes_iter())
    
    def add_edge(self, nodes, direction=None, label=u"0"):
        assert not filter(lambda n: not n.startswith(u"n_"), nodes)
        
        nodes_set = set(nodes)
        if len(nodes_set) < 3:
            edge_id = u"e_" + unicode(self.next_edge_index)
            self.next_edge_index += 1
        else:
            edge_id = u"he_" + unicode(self.next_hedge_index)
            self.next_hedge_index += 1
        
        if not direction:
            direction = set(permutations(nodes_set))
        
        self.bipartite_graph.add_node(edge_id, direction=direction, labels=[label], bipartite=1)
        for node in nodes:
            self.bipartite_graph.add_edge(edge_id, node)
    
    def remove_node(self, node):
        assert node.startswith(u"n_")
        
        connected_edges = self.bipartite_graph.neighbors(node)
        self.bipartite_graph.remove_node(node)
        self.bipartite_graph.remove_nodes_from(connected_edges)
    
    def remove_nodes_from(self, nodes):
        for node in nodes:
            self.remove_node(node)
    
    def remove_edge(self, edge_id):
        assert edge_id.startswith(u"e_") or edge_id.startswith(u"he_")
        self.bipartite_graph.remove_node(edge_id)
    
    def remove_edges_from(self, edge_ids):
        self.bipartite_graph.remove_nodes_from(edge_ids)
    
    def edge(self, edge_id):
        assert edge_id.startswith(u"e_") or edge_id.startswith(u"he_")
        return self.bipartite_graph.node[edge_id]
    
    def edges_iter(self):
        return filter(lambda node: self.bipartite_graph.node[node]["bipartite"] == 1, self.bipartite_graph.nodes_iter())
    
    def edges_2_iter(self):
        return filter(lambda edge_id: len(self.endpoints(edge_id)) == 2, self.edges_iter())
    
    def edges_2(self):
        return list(self.edges_2_iter())
    
    def edges(self, u=None, v=None):
        if u:
            assert u.startswith(u"n_")
            
            u_edges = self.bipartite_graph.neighbors(u)
            if not v:
                return u_edges
            
            assert v.startswith(u"n_")
            edges = []
            for edge in u_edges:
                adj_nodes = self.bipartite_graph.neighbors(edge)
                if v in adj_nodes:
                    edges.append(edge)
            return edges
        else:
            return list(self.edges_iter())
    
    def hedges_iter(self):
        return filter(lambda edge: edge.startswith(u"he_"), self.edges_iter())
    
    def hedges(self, u=None, v=None, w=None):
        if u:
            assert u.startswith(u"n_")
            if v:
                assert v.startswith(u"n_")
                if w:
                    assert w.startswith(u"n_")
            
            u_edges = self.bipartite_graph.neighbors(u)
            u_hedges = filter(lambda edge: edge.startswith(u"he_"), u_edges)
            if len(u_hedges) == 0:
                return []
            elif not v:
                return u_hedges
            else:
                if not w:
                    hedges = []
                    for hedge in u_hedges:
                        nodes = self.bipartite_graph.neighbors(hedge)
                        if v in nodes:
                            hedges.append(hedge)
                    return hedges
                else:
                    hedges = []
                    for hedge in u_hedges:
                        nodes = self.bipartite_graph.neighbors(hedge)
                        if not set(nodes) ^ set(u, v, w):
                            hedges.append(hedge)
                    return hedges
        else:
            return list(self.hedges_iter())
    
    def degree(self, node):
        assert node.startswith(u"n_")
        return self.bipartite_graph.degree(node)
    
    def neighbors(self, node):
        assert node.startswith(u"n_")
        
        edges = self.bipartite_graph.neighbors(node)
        neighbors = map(lambda edge: self.bipartite_graph.neighbors(edge), edges)
        return list(set(itertools.chain(*neighbors)) - set([node]))
    
    def endpoints(self, edge_id):
        assert edge_id.startswith(u"e_") or edge_id.startswith(u"he_")
        
        return self.bipartite_graph.neighbors(edge_id)
    
    def subgraph(self, nodes, multidigraph=False):
        if not multidigraph:
            subgraph = nx.Graph()
        else:
            subgraph = nx.MultiDiGraph()
        
        for node in nodes:
            assert node.startswith(u"n_")
            subgraph.add_node(node, attr_dict=self.bipartite_graph.node[node])
        
        set_nodes = set(nodes)
        
        if not multidigraph:
            for u in nodes:
                neighbors = self.neighbors(u)
                for v in neighbors:
                    if v in set_nodes:
                        edge = self.edge(self.edges(u, v)[0])
                        # TODO: how do we deal with the label of hyperedges?
                        subgraph.add_edge(u, v, label=edge["labels"][0])
        else:
            for u in nodes:
                neighbors = self.neighbors(u)
                for v in neighbors:
                    if v in set_nodes:
                        edge_ids = self.edges(u, v)
                        for edge_id in edge_ids:
                            edge_attr = self.edge(edge_id)
                            edge_dir = self.edge_dir_code(edge_attr["direction"], u, v)
                            # TODO: how do we deal with the label of hyperedges?
                            if edge_dir >= 0:
                                subgraph.add_edge(u, v, label=edge_attr["labels"][0])
                            if edge_dir <= 0:
                                subgraph.add_edge(v, u, label=edge_attr["labels"][0])
        
        return subgraph
    
    def self_loops(self):
        return filter(lambda edge_id: self.bipartite_graph.degree(edge_id) == 1, self.edges_iter())
    
    def to_graph(self, multidigraph=False):
        return self.subgraph(self.nodes(), multidigraph=multidigraph)
    
    def visualize(self):
        nxext.visualize_graph(self.bipartite_graph, bipartite=True, edge_labels=False)

    def __init__(self, nx_graph):
        self.bipartite_graph = nx.Graph()
        self.node = self.bipartite_graph.node
        self.next_edge_index = 0
        self.next_hedge_index = 0
        
        # add nodes
        for node in nx_graph.nodes_iter():
            self.bipartite_graph.add_node(u"n_{0}".format(node), attr_dict=nx_graph.node[node], bipartite=0)
        
        # add edges of order 2
        if nx_graph.is_directed():
            adj_nodes = nxext.get_all_adjacent_nodes(nx_graph)
            for pair in adj_nodes:
                edges = nxext.get_edge_labels_and_dirs(nx_graph, pair[0], pair[1])
                u = u"n_{0}".format(pair[0])
                v = u"n_{0}".format(pair[1])
                for edge in edges:
                    dir_code = edge[1]
                    if dir_code == 0:
                        direction = None
                    elif dir_code > 0:
                        direction = set([(u, v)])
                    else:
                        direction = set([(v, u)])
                    self.add_edge(set([u, v]), direction=direction, label=edge[0])
        else:
            for edge_endpoints in nx_graph.edges_iter():
                u = u"n_{0}".format(edge_endpoints[0])
                v = u"n_{0}".format(edge_endpoints[1])
                if nx_graph.is_multigraph():
                    edges = nx_graph[edge_endpoints[0]][edge_endpoints[1]]
                    for i in range(len(edges)):
                        self.add_edge(set([u, v]), label=edges[i]["label"])
                else:
                    edge_label = nx_graph.edge[edge_endpoints[0]][edge_endpoints[1]]["label"]
                    self.add_edge(set([u, v]), label=edge_label)
        