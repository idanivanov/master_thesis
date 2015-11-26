'''
Created on Oct 29, 2015

@author: Ivan Ivanov

Represents a hypergraph with hyperedges of order at most 3.
'''

from networkx.algorithms import bipartite
from itertools import permutations, groupby
from ivanov.graph import nxext
from timeit import itertools
import networkx as nx
import copy
import time

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
        return self.nodes_count
    
    def number_of_edges(self):
        return self.edges_count
    
    def number_of_hedges(self):
        return self.hedges_count
    
    def add_node(self, node, attr_dict):
        node_id = u"n_{0}".format(node)
        self.bipartite_graph.add_node(node_id, attr_dict=attr_dict, bipartite=0)
        if len(attr_dict["labels"]) > 1:
            self.nodes_with_more_labels.append(node_id)
        self.nodes_count += 1
    
    def nodes_iter(self):
        return filter(lambda node: self.bipartite_graph.node[node]["bipartite"] == 0, self.bipartite_graph.nodes_iter())
        
    def nodes(self):
        return list(self.nodes_iter())
    
    def add_edge(self, nodes, direction=None, label=u"0", init_mode=False):
        assert not filter(lambda n: not n.startswith(u"n_"), nodes)
        
        nodes_set = set(nodes)
        if len(nodes_set) < 3:
            edge_id = u"e_" + unicode(self.next_edge_index)
            is_hedge = False
            self.next_edge_index += 1
        else:
            edge_id = u"he_" + unicode(self.next_hedge_index)
            is_hedge = True
            self.next_hedge_index += 1
            self.hedges_count += 1
        
        if not direction:
            direction = set(permutations(nodes_set))
        
        self.bipartite_graph.add_node(edge_id, direction=direction, labels=[label], bipartite=1)
        self.edges_count += 1
        
        for node in nodes:
            self.bipartite_graph.add_edge(edge_id, node)
        
        # update self loops
        if len(nodes_set) == 1:
            self.self_loops.add(edge_id)
        
        if not init_mode:
            # update parallel edges
            endpoints = list(nodes)
            if is_hedge:
                self.check_for_parallel_hedges(endpoints[0], endpoints[1], endpoints[2])
            else:
                self.check_for_parallel_edges(endpoints[0], endpoints[1])
            
            # update nodes with n neighbors sets
            self.update_nodes_with_n_neighbors(nodes_set)
    
    def remove_node(self, node):
        assert node.startswith(u"n_")
        
        connected_edges = self.bipartite_graph.neighbors(node)
        self.remove_edges_from(connected_edges)
        self.bipartite_graph.remove_node(node)
        self.nodes_count -= 1
        if node in self.nodes_with_more_labels: 
            self.nodes_with_more_labels.remove(node)
        self.remove_from_nodes_with_n_neighbors(set([node]))
    
    def remove_nodes_from(self, nodes):
        for node in nodes:
            self.remove_node(node)
    
    def remove_edge(self, edge_id):
        assert edge_id.startswith(u"e_") or edge_id.startswith(u"he_")
        
        endpoints = set(self.endpoints(edge_id))
        
        # update parallel edges
        if edge_id.startswith(u"e_"):
            self.try_remove_from_parallel_edges_groups(edge_id)
        else:
            self.try_remove_from_parallel_hedges_groups(edge_id)
        
        self.bipartite_graph.remove_node(edge_id)
        self.edges_count -= 1
        
        # update self loops
        if edge_id in self.self_loops:
            self.self_loops.remove(edge_id)
        
        # update nodes with n neighbors sets
        self.update_nodes_with_n_neighbors(endpoints)
    
    def remove_edges_from(self, edge_ids):
        for edge_id in list(edge_ids):
            self.remove_edge(edge_id)
    
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
    
    def subgraph(self, nodes):
        assert type(nodes) is set

        subgraph = nx.Graph()
        
        for node in nodes:
            assert node.startswith(u"n_")
            subgraph.add_node(node, attr_dict=self.bipartite_graph.node[node])
        
        checked = set()
        
        for u in nodes:
            neighbors = self.neighbors(u)
            for v in neighbors:
                if v in nodes and v not in checked:
                    subgraph.add_edge(u, v)
            checked.add(u)
        
        return subgraph
    
    def add_node_label(self, node_id, label):
        assert node_id.startswith(u"n_")
        
        labels = self.bipartite_graph.node[node_id]["labels"]
        labels.append(label)
        if len(labels) > 1:
            self.nodes_with_more_labels.add(node_id)
    
    def set_node_labels(self, node_id, labels):
        assert node_id.startswith(u"n_")
        assert type(labels) is list
        
        self.bipartite_graph.node[node_id]["labels"] = labels
        if len(labels) > 1:
            self.nodes_with_more_labels.add(node_id)
        else:
            if node_id in self.nodes_with_more_labels:
                self.nodes_with_more_labels.remove(node_id)
    
    def reset_nodes_with_more_labels(self):
        self.nodes_with_more_labels = set()
    
    def init_parallel_edges_groups(self):
        self.reset_parallel_edges_groups()
        self.update_parallel_edges_groups(self.edges_2_iter())
    
    def try_remove_from_parallel_edges_groups(self, edge_id):
        key = u",".join(sorted(self.endpoints(edge_id)))
        if key in self.parallel_edges_groups:
            edges = self.parallel_edges_groups[key]
            if edge_id in edges:
                if len(edges) < 2:
                    del self.parallel_edges_groups[key]
                else:
                    edges.remove(edge_id)
    
    def update_parallel_edges_groups(self, new_edges):
        new_keys = []
        for edge in new_edges:
            assert edge.startswith(u"e_")
            key = u",".join(sorted(self.endpoints(edge)))
            if self.parallel_edges_groups.has_key(key):
                self.parallel_edges_groups[key].append(edge)
            else:
                self.parallel_edges_groups[key] = [edge]
            new_keys.append(key)
        for key in new_keys:
            if len(self.parallel_edges_groups[key]) < 2:
                del self.parallel_edges_groups[key]
    
    def check_for_parallel_edges(self, u, v):
        par_edges = self.edges(u, v)
        if len(par_edges) > 1:
            key = u",".join(sorted([u, v]))
            self.parallel_edges_groups[key] = set(par_edges)
    
    def reset_parallel_edges_groups(self):
        self.parallel_edges_groups = {}
    
    def init_parallel_hedges_groups(self):
        self.reset_parallel_hedges_groups()
        self.update_parallel_hedges_groups(self.hedges_iter())
    
    def try_remove_from_parallel_hedges_groups(self, hedge_id):
        key = u",".join(sorted(self.endpoints(hedge_id)))
        if key in self.parallel_hedges_groups:
            hedges = self.parallel_hedges_groups[key]
            if hedge_id in hedges:
                if len(hedges) < 2:
                    del self.parallel_hedges_groups[key]
                else:
                    hedges.remove(hedge_id)
    
    def update_parallel_hedges_groups(self, new_hedges):
        new_keys = []
        for hedge in new_hedges:
            assert hedge.startswith(u"e_")
            key = u",".join(sorted(self.endpoints(hedge)))
            if self.parallel_hedges_groups.has_key(key):
                self.parallel_hedges_groups[key].append(hedge)
            else:
                self.parallel_hedges_groups[key] = [hedge]
            new_keys.append(key)
        for key in new_keys:
            if len(self.parallel_hedges_groups[key]) < 2:
                del self.parallel_hedges_groups[key]
    
    def check_for_parallel_hedges(self, u, v, w):
        par_hedges = self.hedges(u, v, w)
        if len(par_hedges) > 1:
            key = u",".join(sorted([u, v, w]))
            self.parallel_hedges_groups[key] = par_hedges
    
    def reset_parallel_hedges_groups(self):
        self.parallel_hedges_groups = {}
    
    def reset_self_loops(self):
        self.self_loops = set()
    
    def init_nodes_with_n_neighbors(self):
        self.reset_nodes_with_n_neighbors()
        
        for node in self.nodes_iter():
            neighbors_count = len(self.neighbors(node))
            if neighbors_count == 1:
                self.nodes_with_1_neighbor.add(node)
            elif neighbors_count == 2:
                self.nodes_with_2_neighbors.add(node)
            elif neighbors_count == 3:
                self.nodes_with_3_neighbors.add(node)
    
    def update_nodes_with_n_neighbors(self, candidate_nodes):
        assert type(candidate_nodes) is set
        
        new_nodes_with_1_neighbor = set()
        new_nodes_with_2_neighbors = set()
        new_nodes_with_3_neighbors = set()
        for node in candidate_nodes:
            neighbors_count = len(self.neighbors(node))
            if neighbors_count == 1:
                new_nodes_with_1_neighbor.add(node)
            elif neighbors_count == 2:
                new_nodes_with_2_neighbors.add(node)
            elif neighbors_count == 3:
                new_nodes_with_3_neighbors.add(node)
        
        self.nodes_with_1_neighbor |= new_nodes_with_1_neighbor
        self.nodes_with_1_neighbor -= candidate_nodes - new_nodes_with_1_neighbor
        
        self.nodes_with_2_neighbors |= new_nodes_with_2_neighbors
        self.nodes_with_2_neighbors -= candidate_nodes - new_nodes_with_2_neighbors
        
        self.nodes_with_3_neighbors |= new_nodes_with_3_neighbors
        self.nodes_with_3_neighbors -= candidate_nodes - new_nodes_with_3_neighbors
    
    def remove_from_nodes_with_n_neighbors(self, nodes):
        assert type(nodes) is set
        
        self.nodes_with_1_neighbor -= nodes
        self.nodes_with_2_neighbors -= nodes
        self.nodes_with_3_neighbors -= nodes
    
    def reset_nodes_with_n_neighbors(self):
        self.nodes_with_1_neighbor = set()
        self.nodes_with_2_neighbors = set()
        self.nodes_with_3_neighbors = set()
    
    def to_graph(self, multidigraph=False):
        return self.subgraph(self.nodes(), multidigraph=multidigraph)
    
    def visualize(self):
        nxext.visualize_graph(self.bipartite_graph, bipartite=True, edge_labels=False)

    def __init__(self, nx_graph):
        self.bipartite_graph = nx.Graph()
        self.node = self.bipartite_graph.node
        self.next_edge_index = 0
        self.next_hedge_index = 0
        
        self.nodes_count = 0
        self.edges_count = 0
        self.hedges_count = 0
        
        # ready sets
        self.reset_nodes_with_more_labels()
        self.reset_self_loops()
        self.reset_parallel_hedges_groups()
        
        print "Adding nodes..."
        start = time.time()
        # add nodes
        for node in nx_graph.nodes_iter():
            self.add_node(node, attr_dict=copy.deepcopy(nx_graph.node[node]))
        end = time.time()
        print "Adding nodes took {0} s.".format(end - start)
        
        print "Adding edges..."
        start = time.time()
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
                    self.add_edge(set([u, v]), direction=direction, label=copy.deepcopy(edge[0]), init_mode=True)
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
                    self.add_edge(set([u, v]), label=copy.deepcopy(edge_label), init_mode=True)
        end = time.time()
        print "Adding edges took {0} s.".format(end - start)
        
        
        # Initialize ready sets
        print "Init parallel edges..."
        start = time.time()
        self.init_parallel_edges_groups()
        end = time.time()
        print "Init parallel hedges took {0} s.".format(end - start)
        
        print "Init nodes with n neighbors..."
        start = time.time()
        self.init_nodes_with_n_neighbors()
        end = time.time()
        print "Init nodes with n neighbors took {0} s.".format(end - start)
