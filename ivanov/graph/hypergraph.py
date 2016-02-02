'''
Created on Oct 29, 2015

@author: Ivan Ivanov

Represents a hypergraph with hyperedges of order at most 3.
'''

from itertools import permutations, combinations
from ivanov.inout.serializable import Serializable
from ivanov.graph import nxext
from timeit import itertools
import networkx as nx
import copy

class Hypergraph(Serializable):
        
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
    
    @staticmethod
    def format_node_id(node):
        if unicode(node).startswith(u"n_"):
            return node
        else:
            return u"n_{0}".format(node)
    
    def number_of_nodes(self):
        return self.nodes_count
    
    def number_of_edges(self):
        return self.edges_count
    
    def number_of_hedges(self):
        return self.hedges_count
    
    def add_node(self, node, attr_dict):
        node_id = Hypergraph.format_node_id(node)
        self.bipartite_graph.add_node(node_id, attr_dict=attr_dict, bipartite=0)
        if len(attr_dict["labels"]) > 1:
            self.nodes_with_more_labels.add(node_id)
        self.nodes_count += 1
    
    def has_node(self, node):
        assert node.startswith(u"n_")
        return self.bipartite_graph.has_node(node)
    
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
        
        return edge_id
        
    def remove_node(self, node):
        assert node.startswith(u"n_")
        
        connected_edges = self.bipartite_graph.neighbors(node)
        self.remove_edges_from(connected_edges)
        self.bipartite_graph.remove_node(node)
        self.nodes_count -= 1
    
    def remove_nodes_from(self, nodes):
        for node in nodes:
            self.remove_node(node)
    
    def remove_edge(self, edge_id):
        assert edge_id.startswith(u"e_") or edge_id.startswith(u"he_")
        
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
    
    def remove_edges_from(self, edge_ids):
        for edge_id in list(edge_ids):
            self.remove_edge(edge_id)
    
    def has_edge(self, u, v, dir_code=0):
        assert u.startswith(u"n_") and v.startswith(u"n_")
        if next(self.edges_iter_dir(u, v, dir_code), None):
            return True
        else:
            return False
    
    def edge(self, edge_id):
        assert edge_id.startswith(u"e_") or edge_id.startswith(u"he_")
        return self.bipartite_graph.node[edge_id]
    
    def edges(self, u=None, v=None):
        return list(self.edges_iter(u, v))
    
    def edges_2_iter(self):
        for edge in self.edges_iter():
            if len(self.endpoints(edge)) == 2:
                yield edge
    
    def edges_2(self):
        return list(self.edges_2_iter())
    
    def edges_iter(self, u=None, v=None):
        def all_edges():
            for x in self.bipartite_graph.nodes_iter():
                if self.bipartite_graph.node[x]["bipartite"] == 1:
                    yield x
        def edges_of_u_v(_u_edges, _v):
            for edge in u_edges:
                if v in self.endpoints(edge):
                    yield edge
        
        if u:
            assert u.startswith(u"n_")
            u_edges = self.bipartite_graph.neighbors_iter(u)
            if not v:
                return u_edges
            
            assert v.startswith(u"n_")
            return edges_of_u_v(u_edges, v)
        else:
            return all_edges()
    
    def edges_iter_dir(self, u, v=None, dir_code=0):
        '''Get edges incident to node u filtered by direction.
        :param u: node id.
        :param dir_code: Direction code - If 0 all edges are
        returned, if 1 only outgoing edges are returned,
        if -1 only incoming edges are returned.
        '''
        def filter_edges():
            if dir_code < 0:
                for edge in self.edges_iter(u, v):
                    edge_dir = self.edge(edge)["direction"]
                    if any(map(lambda dir_perm: dir_perm.index(u) > 0, edge_dir)):
                        yield edge
            elif dir_code > 0:
                for edge in self.edges_iter(u, v):
                    edge_dir = self.edge(edge)["direction"]
                    if any(map(lambda dir_perm: dir_perm.index(u) < len(dir_perm) - 1, edge_dir)):
                        yield edge
        
        if dir_code == 0:
            return self.edges_iter(u, v)
        else:
            return filter_edges()
    
    def hedges_iter(self):
        for edge in self.edges_iter():
            if edge.startswith(u"he_"):
                yield edge
    
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
                        if not set(nodes) ^ set([u, v, w]):
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
    
    def get_adj_nodes(self, nodes):
        assert type(nodes) is set
        
        all_edges = set()
        for node in nodes:
            edges = set(self.bipartite_graph.neighbors(node))
            all_edges |= edges
        
        adj_nodes = set()
        for edge in all_edges:
            endpoints = self.bipartite_graph.neighbors(edge)
            for pair in combinations(endpoints, 2):
                if pair[0] in nodes and pair[1] in nodes:
                    adj_nodes.add(tuple(sorted(pair)))
        
        return adj_nodes
    
    def subgraph(self, nodes):
        assert type(nodes) is set

        subgraph = nx.Graph()
        
        for node in nodes:
            assert node.startswith(u"n_")
            subgraph.add_node(node)
        
        for pair in self.get_adj_nodes(nodes):
            subgraph.add_edge(pair[0], pair[1])
        
        return subgraph
    
    # TODO: This method can be optimized
    # hyperedges are shown as 3 edges
    def subgraph_with_labels(self, nodes):
        assert type(nodes) is set

        subgraph = nx.MultiDiGraph()
        
        for node in nodes:
            assert node.startswith(u"n_")
            subgraph.add_node(node, labels=self.node[node]["labels"])
        
        for pair in self.get_adj_nodes(nodes):
            edges = self.edges(pair[0], pair[1])
            for edge in edges:
                edge_attr = self.edge(edge)
                if not any(map(lambda dir_perm: dir_perm.index(pair[0]) < dir_perm.index(pair[1]), edge_attr["direction"])):
                    # edge direction = -1
                    subgraph.add_edge(pair[1], pair[0], label=edge_attr["labels"][0])
                elif not any(map(lambda dir_perm: dir_perm.index(pair[0]) > dir_perm.index(pair[1]), edge_attr["direction"])):
                    # edge direction = 1
                    subgraph.add_edge(pair[0], pair[1], label=edge_attr["labels"][0])
                else:
                    # edge direction = 0
                    subgraph.add_edge(pair[0], pair[1], label=edge_attr["labels"][0])
                    subgraph.add_edge(pair[1], pair[0], label=edge_attr["labels"][0])
        
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
        self.update_parallel_edges_groups(self.edges_2_iter(), init_mode=True)
    
    def try_remove_from_parallel_edges_groups(self, edge_id):
        key = u",".join(sorted(self.endpoints(edge_id)))
        if key in self.parallel_edges_groups:
            edges = self.parallel_edges_groups[key]
            if edge_id in edges:
                if len(edges) < 2:
                    del self.parallel_edges_groups[key]
                else:
                    edges.remove(edge_id)
    
    def update_parallel_edges_groups(self, new_edges, init_mode=False):
        if init_mode:
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
        else:
            checked_endpoints = set()
            for edge_id in new_edges:
                assert edge_id.startswith(u"e_")
                if edge_id not in self.self_loops:
                    endpoints = tuple(sorted(self.endpoints(edge_id)))
                    if endpoints not in checked_endpoints:
                        checked_endpoints.add(endpoints)
                        self.check_for_parallel_edges(endpoints[0], endpoints[1])
    
    def check_for_parallel_edges(self, u, v):
        par_edges = filter(lambda edge_id: edge_id.startswith(u"e_"), self.edges(u, v))
        if len(par_edges) > 1:
            key = u",".join(sorted([u, v]))
            self.parallel_edges_groups[key] = set(par_edges)
    
    def reset_parallel_edges_groups(self):
        self.parallel_edges_groups = {}
    
    def init_parallel_hedges_groups(self):
        self.reset_parallel_hedges_groups()
        self.update_parallel_hedges_groups(self.hedges_iter(), init_mode=True)
    
    def try_remove_from_parallel_hedges_groups(self, hedge_id):
        key = u",".join(sorted(self.endpoints(hedge_id)))
        if key in self.parallel_hedges_groups:
            hedges = self.parallel_hedges_groups[key]
            if hedge_id in hedges:
                if len(hedges) < 2:
                    del self.parallel_hedges_groups[key]
                else:
                    hedges.remove(hedge_id)
    
    def update_parallel_hedges_groups(self, new_hedges, init_mode=False):
        if init_mode:
            new_keys = []
            for hedge in new_hedges:
                assert hedge.startswith(u"he_")
                key = u",".join(sorted(self.endpoints(hedge)))
                if self.parallel_hedges_groups.has_key(key):
                    self.parallel_hedges_groups[key].append(hedge)
                else:
                    self.parallel_hedges_groups[key] = [hedge]
                new_keys.append(key)
            for key in new_keys:
                if len(self.parallel_hedges_groups[key]) < 2:
                    del self.parallel_hedges_groups[key]
        else:
            checked_endpoints = set()
            for hedge_id in new_hedges:
                assert hedge_id.startswith(u"he_")
                if hedge_id not in self.self_loops:
                    endpoints = tuple(sorted(self.endpoints(hedge_id)))
                    if endpoints not in checked_endpoints:
                        checked_endpoints.add(endpoints)
                        self.check_for_parallel_hedges(endpoints[0], endpoints[1], endpoints[2])
    
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
            if self.bipartite_graph.has_node(node):
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
    
    def to_nx_graph(self):
        return self.subgraph_with_labels(set(self.nodes_iter()))
    
    def visualize(self):
        nxext.visualize_graph(self.bipartite_graph, bipartite=True, edge_labels=False)
    
    def copy(self):
        return copy.deepcopy(self)
    
    # NOTE: does not check isomorphism
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            self_dict = dict(self.__dict__)
            other_dict = dict(other.__dict__)
            # do not compare networkx graphs
            del self_dict["bipartite_graph"]
            del other_dict["bipartite_graph"]
            return self_dict == other_dict
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __init__(self, nx_graph = nx.Graph()):
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
        
        # add nodes
        for node in nx_graph.nodes_iter():
            self.add_node(node, attr_dict=copy.deepcopy(nx_graph.node[node]))
        
        # add edges of order 2
        if nx_graph.is_directed():
            adj_nodes = nxext.get_all_adjacent_nodes(nx_graph)
            for pair in adj_nodes:
                edges = nxext.get_edge_labels_and_dirs(nx_graph, pair[0], pair[1])
                u = Hypergraph.format_node_id(pair[0])
                v = Hypergraph.format_node_id(pair[1])
                for edge in edges:
                    dir_code = edge[1]
                    if dir_code == 0:
                        direction = None
                    elif dir_code > 0:
                        direction = set([(u, v)])
                    else:
                        direction = set([(v, u)])
                    self.add_edge(set([u, v]), direction=direction, label=copy.deepcopy(edge[0]))
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
                    self.add_edge(set([u, v]), label=copy.deepcopy(edge_label))
        
        # Initialize ready sets
        self.init_parallel_edges_groups()
        self.init_nodes_with_n_neighbors()
