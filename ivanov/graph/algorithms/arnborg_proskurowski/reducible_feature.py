'''
Created on Oct 7, 2015

@author: Ivan Ivanov
'''

from itertools import combinations, permutations
from networkx.classes.function import neighbors
from ivanov.graph.hypergraph import Hypergraph
from ivanov.graph import nxext
import networkx as nx
import itertools
import sys

class ReducibleFeature(object):
    
    # public static methods
    
    @staticmethod
    def extract_rule_1_features(hypergraph):        
        pendant_nodes_and_dipoles_subgraph = hypergraph.subgraph(hypergraph.nodes_with_1_neighbor)
        cc = nx.connected_components(nx.Graph(pendant_nodes_and_dipoles_subgraph))
        
        for comp in cc:
            comp_list = list(comp)
            if len(comp_list) > 1:
                if len(comp_list) > 2:
                    sys.stderr.write("\n[ReducibleFeature] Error: Wrong nodes extracted.")
                else:
                    # dipole
                    yield ReducibleFeature(1, 1, [comp_list[0]], [comp_list[1]])
            else:
                neighbor = hypergraph.neighbors(comp_list[0])[0]
                if comp_list[0] != neighbor: # skip self-loops
                    # pendant
                    yield ReducibleFeature(1, 2, [comp_list[0]], [neighbor])
    
    @staticmethod
    def extract_rule_2_features(hypergraph):
        series_subgraph = hypergraph.subgraph(hypergraph.nodes_with_2_neighbors)
        
        # ring
        rings = nx.cycle_basis(series_subgraph)
        for ring in rings:
            yield ReducibleFeature(2, 2, ring[1:], [ring[0]])
        
        nodes_in_rings = itertools.chain(*rings)
        series_subgraph.remove_nodes_from(nodes_in_rings)
        
        # chain
        def get_distinct_paths(graph_of_paths):
            cc = nx.connected_components(graph_of_paths)
            for comp in cc:
                if len(comp) > 1:
                    endpoints = filter(lambda node: len(nxext.get_all_neighbors(graph_of_paths, node)) == 1, comp)
                    assert len(endpoints) == 2
                    yield nx.shortest_path(graph_of_paths, endpoints[0], endpoints[1])
                else:
                    yield list(comp)
        
        for path in get_distinct_paths(series_subgraph):
            if len(path) < 2:
                neighbors = hypergraph.neighbors(path[0])
                yield ReducibleFeature(2, 1, path, neighbors)
            else:
                source = path[0]
                target = path[-1]
                source_neighbors = hypergraph.neighbors(source)
                target_neighbors = hypergraph.neighbors(target)
                s = source_neighbors[0] if source_neighbors[1] == path[1] else source_neighbors[1]
                t = target_neighbors[0] if target_neighbors[1] == path[-2] else target_neighbors[1]
                yield ReducibleFeature(2, 1, path, [s, t])
    
    @staticmethod
    def extract_degree_3_features(hypergraph):
        def get_triangles(nodes_with_3_neighbors):
            def is_triangle(node_with_3_neighbors):
                neighbors = node_with_3_neighbors[1]
                for pair in combinations(neighbors, 2):
                    if len(hypergraph.edges(pair[0], pair[1])) > 0:
                        return True
                return False
            
            return map(lambda neighborhood: ([neighborhood[0]], neighborhood[1]), filter(is_triangle, nodes_with_3_neighbors))
        
        def get_buddies(nodes_with_3_neighbors):
            already_checked = []
            for neighborhood in nodes_with_3_neighbors:
                node = neighborhood[0]
                if node not in already_checked:
                    neighbors = neighborhood[1]
                    neighbors_of_neighbors = map(lambda neighbor: set(hypergraph.neighbors(neighbor)), neighbors)
                    common_neighbors = reduce(lambda set1, set2: set1 & set2, neighbors_of_neighbors)
                    
                    buddy_nodes = [node]
                    for potential_buddy_node in common_neighbors:
                        if potential_buddy_node != node and filter(lambda neigh: neigh[0] == potential_buddy_node, nodes_with_3_neighbors):
                            buddy_nodes.append(potential_buddy_node)
                            already_checked += buddy_nodes
                    
                    if len(buddy_nodes) < 2:
                        continue
                    
#                     # TODO: should we have multiple buddy nodes?
#                     for pair in combinations(buddy_nodes, 2):
#                         yield (pair, neighbors)
                    yield (buddy_nodes, neighbors)
        
        # TODO: We consider also hubs with degree larger than 3. Is this correct?
        def get_cubes(nodes_with_3_neighbors):
            nodes_degree_3 = set(map(lambda neighborhood: neighborhood[0], nodes_with_3_neighbors))
            already_checked_hubs = []
            for neighborhood in nodes_with_3_neighbors:
                neighbors = neighborhood[1]
                neighbors_of_neighbors = {neighbor: set(hypergraph.neighbors(neighbor)) for neighbor in neighbors}
                for neigh in neighbors_of_neighbors.items():
                    # TODO: not sure about this condition, the definition of a hub in the paper is unclear
                    if neigh[1].intersection(nodes_degree_3) == neigh[1] and neigh[0] not in already_checked_hubs:
                        already_checked_hubs.append(neigh[0])
                        hub_periphery = neigh[1]
                        neighbors_of_hub_neighbors = {node: set(hypergraph.neighbors(node)) - set([neigh[0]]) for node in hub_periphery}
                        
                        # the periphery should form a ring
                        cube_peripheral_nodes = set([])
                        for n in neighbors_of_hub_neighbors.items():
                            cube_peripheral_nodes = cube_peripheral_nodes.union(n[1])
                        hub_ring_periphery = hub_periphery.union(cube_peripheral_nodes)
                        periphery_subgraph = nx.Graph(hypergraph.subgraph(hub_ring_periphery))
                        cycle = nx.cycle_basis(periphery_subgraph)
                        if len(cycle) != 1:
                            continue
                        elif len(cycle[0]) != len(hub_periphery) * 2:
                            # the ring around the hub should be of alternating reducible and peripheral nodes
                            continue
                        
                        # there should be no mutually-adjacent neighbors in the periphery
                        hub_periphery_pairs = combinations(hub_periphery, 2)
                        valid_periphery = True
                        for pair in hub_periphery_pairs:
                            u = pair[0]
                            v = pair[1]
                            if u in neighbors_of_hub_neighbors[v]:
                                valid_periphery = False
                                break
                        
                        if valid_periphery:
                            yield neigh[1], cube_peripheral_nodes.union(set([neigh[0]]))
        
        def get_raw_conflicts_and_isolates(features):
            def get_raw_conflict_and_isolates(features, all_reducibles, checked_features, initial_feature):
                def recursion(conflict_nodes, conflict_periphery, features, all_reducibles, checked_features, feature_to_check, isolates):
                    if feature_to_check in checked_features:
                        return
                     
                    reducible_periphery = set(filter(lambda node: node in all_reducibles, feature_to_check[1]))
                     
                    if len(reducible_periphery) > 0:
                        checked_features.append(feature_to_check)
                        reducibles_set = set(feature_to_check[0])
                        conflict_nodes |= reducibles_set
                        conflict_periphery |= set(feature_to_check[1]) - reducible_periphery
                     
                        for node in reducible_periphery:
                            for node_feature in features:
                                if node in node_feature[0] and node_feature not in checked_features:
                                    recursion(conflict_nodes, conflict_periphery, features, all_reducibles, checked_features, node_feature, isolates)
                     
                    else:
                        isolates.append((feature_to_check[0], feature_to_check[1]))
                     
                    return
                 
                isolates = []
                conflict_nodes = set()
                conflict_periphery = set()
                recursion(conflict_nodes, conflict_periphery, features, all_reducibles, checked_features, initial_feature, isolates)
                return (conflict_nodes, conflict_periphery) if conflict_nodes else None, isolates
             
            all_reducibles = map(lambda feature: feature[0], features)
            all_reducibles = set(itertools.chain(*all_reducibles))
            checked_features = []
            isolates = []
            raw_conflicts = []
             
            for feature in features:
                conflict_feature, new_isolates = get_raw_conflict_and_isolates(features, all_reducibles, checked_features, feature)
                isolates += new_isolates
                if conflict_feature:
                    raw_conflicts.append(conflict_feature)
                     
            return raw_conflicts, isolates
        
        def get_triangle_conflicts(triangles):
            def _identify_conflicts_and_isolates(raw_conflicts, raw_isolates):
                conflicts = []
                isolates = map(lambda isolate: ReducibleFeature(4, 1, isolate[0], isolate[1]), raw_isolates)
                
                # Identify conflicts (and possible isolates)
                for raw_conflict in raw_conflicts:
                    conflict_subgraph = nx.Graph(hypergraph.subgraph(raw_conflict[0] | raw_conflict[1]))
                    nodes_in_subgraph = conflict_subgraph.number_of_nodes()
                    len_reducible = len(raw_conflict[0])
                    len_periphery = len(raw_conflict[1])
    #                 NxExtensions.visualize_graph(conflict_subgraph)
                     
                    # Rule 5.1 - Diamonds (or isolates)
                    if nodes_in_subgraph == 4:
                        if len_periphery == 3:
                            if conflict_subgraph.number_of_edges() >= 4:
                                # Rule 4.1 (isolate triangle)
                                isolates.append(ReducibleFeature(4, 1, raw_conflict[0], raw_conflict[1]))
                                continue
                            else:
                                sys.stderr.write("\n[ReducibleFeature] Unrecognized triangle conflict containing 1 reducible node and < 4 edges.")
                        elif len_periphery == 2:
                            periphery_list = list(raw_conflict[1])
                            if not conflict_subgraph.has_edge(periphery_list[0], periphery_list[1]):
                                # Rule 5.1.2
                                conflicts.append(ReducibleFeature(5, 1, raw_conflict[0], raw_conflict[1], subsubrule = 2))
                                continue
                        # Rule 5.1.1
                        conflicts.append(ReducibleFeature(5, 1, raw_conflict[0], raw_conflict[1], subsubrule = 1))
                        continue
                     
                    # reducible_subgraph = H (from rule 5.2 in the paper of A&P)
                    reducible_subgraph = conflict_subgraph.subgraph(raw_conflict[0])
                    reducible_degrees = set(reducible_subgraph.degree().values())
                     
                    if len(reducible_degrees) == 1:
                        reducible_degree = next(iter(reducible_degrees))
                         
                        if reducible_degree == 1:
                            # Rule 5.2.1
                            if len_reducible == 2:
                                if len(raw_conflict[1]) == 4:
                                    # TODO: we skip the 4-vertex separator case. Is this correct?
                                    continue
                                conflicts.append(ReducibleFeature(5, 2, raw_conflict[0], raw_conflict[1], subsubrule = 1))
                                continue
                            else:
                                sys.stderr.write("\n[ReducibleFeature] Unrecognized feature containing only nodes of degree 1.")
                         
                        elif reducible_degree == 2:
                            # Rule 5.2.3
                            t_edges = []
                            three_cliques = filter(lambda clique: len(clique) == 3, nx.find_cliques_recursive(conflict_subgraph))
                            subgraph_H = conflict_subgraph.subgraph(raw_conflict[0])
                            all_H_edges = map(lambda edge: set([edge[0], edge[1]]), subgraph_H.edges_iter())
                            for clique in three_cliques:
                                new_t_edges = map(lambda edge: set([edge[0], edge[1]]), combinations(set(clique) & raw_conflict[0], 2))
                                t_edges += filter(lambda edge: edge not in t_edges, new_t_edges)
                            f_edges = filter(lambda edge: edge not in t_edges, all_H_edges)
                            def filter_A_vertices(node):
                                neighbors = conflict_subgraph.neighbors(node)
                                has_t = False
                                has_f = False
                                for neighbor in neighbors:
                                    edge = set([node, neighbor])
                                    if edge in t_edges:
                                        has_t = True
                                        if has_f:
                                            break
                                    elif edge in f_edges:
                                        has_f = True
                                        if has_t:
                                            break
                                if has_t and has_f:
                                    return True
                                else:
                                    return False
                            A = set(filter(filter_A_vertices, raw_conflict[0]))
                            if not A:
                                # Rule 5.2.3.1
                                conflicts.append(ReducibleFeature(5, 2, raw_conflict[0], raw_conflict[1], subsubrule = 3, subsubsubrule = 1))
                                continue
                            elif len(A) == len_reducible:
                                # Rule 5.2.3.3
                                if len(raw_conflict[0]) == 4:
                                    # if we have more than 4 reducible nodes the feature is not safely reducible
                                    conflicts.append(ReducibleFeature(5, 2, raw_conflict[0], raw_conflict[1], subsubrule = 3, subsubsubrule = 3))
                                continue
                            else:
                                # Rule 5.2.3.2
                                # TODO: Problem: In the paper this case is presented with reducible nodes which are not adjacent. Are they still in conflict?
                                non_A_nodes = raw_conflict[0] - A
                                non_A_reducible_subgraph = conflict_subgraph.subgraph(non_A_nodes)
                                raw_sub_conflicts = []
                                for comp in nx.connected_components(non_A_reducible_subgraph):
                                    comp_separator = itertools.chain(*map(lambda n: nxext.get_all_neighbors(conflict_subgraph, n), comp))
                                    comp_separator = set(comp_separator) - comp
                                    raw_sub_conflicts.append((comp, comp_separator))
                                sub_conflicts_and_isolates = _identify_conflicts_and_isolates(raw_sub_conflicts, [])
                                for sub_isolate in sub_conflicts_and_isolates["isolates"]:
                                    isolates.append(sub_isolate)
                                for sub_conflict in sub_conflicts_and_isolates["conflicts"]:
                                    conflicts.append(sub_conflict)
                                continue
                         
                        elif reducible_degree == 3:
                            if reducible_subgraph.number_of_nodes() == 6 and reducible_subgraph.number_of_edges() == 9:
                                # Rule 5.2.5 (Prism)
                                conflicts.append(ReducibleFeature(5, 2, raw_conflict[0], raw_conflict[1], subsubrule=5))
                                continue
                            else:
                                # TODO: The explanation in the paper for this case is not clear.
                                # For now extract all possible square configurations from the reducible subgraph.
                                # If there are no squares, the graph is regarded as having tree-width > 3.
                                squares = filter(lambda cycle: len(cycle) == 4, nx.cycle_basis(reducible_subgraph))
                                if squares:
                                    for square in squares:
                                        sq_neigh = set()
                                        for sq_node in square:
                                            neigh = nxext.get_all_neighbors(reducible_subgraph, sq_node)
                                            sq_neigh |= set(neigh)
                                        if len(sq_neigh) == 2:
                                            conflicts.append(ReducibleFeature(5, 2, square, sq_neigh, subsubrule = 3, subsubsubrule = 3))
                                            reducible_subgraph.remove_nodes_from(square)
                                continue
                     
                    else:
                        if 1 in reducible_degrees:
                            # Rule 5.2.2
                            conflicts.append(ReducibleFeature(5, 2, raw_conflict[0], raw_conflict[1], subsubrule = 2))
                            continue
                         
                        else:
                            # Rule 5.2.4
                            conflicts.append(ReducibleFeature(5, 2, raw_conflict[0], raw_conflict[1], subsubrule = 4))
                            continue
                     
                    sys.stderr.write("\n[ReducibleFeature] The conflicting triangles {0} were not handled by any rule.".format(raw_conflicts))
                    conflicts.append(ReducibleFeature(5, 0, raw_conflict[0], raw_conflict[1]))
                         
                return {"isolates": isolates, "conflicts": conflicts}
            
            raw_conflicts, raw_isolates = get_raw_conflicts_and_isolates(triangles)
            return _identify_conflicts_and_isolates(raw_conflicts, raw_isolates)
        
        def get_buddy_conflicts(buddies):
            raw_conflicts, isolates = get_raw_conflicts_and_isolates(buddies)
            conflicts = []
             
            isolates = map(lambda isolate: ReducibleFeature(4, 2, isolate[0], isolate[1]), isolates)
             
            # Identify conflicts
            for raw_conflict in raw_conflicts:
                conflict_subgraph = nx.Graph(hypergraph.subgraph(raw_conflict[0] | raw_conflict[1]))
                nodes_in_subgraph = conflict_subgraph.number_of_nodes()
                len_periphery = len(raw_conflict[1])
#                 NxExtensions.visualize_graph(conflict_subgraph)
                 
                if nodes_in_subgraph == 6:
                    if len_periphery == 2:
                        # Rule 6.2 - Cat's cradle
                        conflicts.append(ReducibleFeature(6, 2, raw_conflict[0], raw_conflict[1]))
                        continue
                    # Rule 6.1 - K(3,3)
                    conflicts.append(ReducibleFeature(6, 1, raw_conflict[0], raw_conflict[1]))
                    continue
                elif nodes_in_subgraph == 5:
                    # this conflict is a wheel which should already be handled by rule 5.2.3.1
                    continue
                 
                sys.stderr.write("\n[ReducibleFeature] The conflicting buddies {0} were not handled by any rule.".format(raw_conflicts))
                conflicts.append(ReducibleFeature(6, 0, raw_conflict[0], raw_conflict[1]))
                     
            return {"isolates": isolates, "conflicts": conflicts}
        
        def get_cube_conflicts(cubes):
            raw_conflicts, isolates = get_raw_conflicts_and_isolates(cubes)
            conflicts = []
             
            isolates = map(lambda isolate: ReducibleFeature(4, 3, isolate[0], isolate[1]), isolates)
             
            # Identify conflicts
            for raw_conflict in raw_conflicts:
                conflict_subgraph = nx.Graph(hypergraph.subgraph(raw_conflict[0] | raw_conflict[1]))
                nodes_in_subgraph = conflict_subgraph.number_of_nodes()
                len_periphery = len(raw_conflict[1])
#                 NxExtensions.visualize_graph(conflict_subgraph)
                 
                if nodes_in_subgraph == 8:
                    # Rule 7.1 - Cube
                    if len_periphery == 0:
                        conflicts.append(ReducibleFeature(7, 1, raw_conflict[0], raw_conflict[1]))
                        continue
                    # Rule 7.2 - Hammock (normal version)
                    elif len_periphery == 2:
                        conflicts.append(ReducibleFeature(7, 2, raw_conflict[0], raw_conflict[1]))
                        continue
                    # Rule 7.2 - Hammock (second version)
                    elif len_periphery == 1 and len(raw_conflict[0]) == 7:
                        # chose one of the neighbors of the peripheral node to create a Hammock
                        peripheral_neighbor = set([conflict_subgraph.neighbors(list(raw_conflict[1])[0])[0]])
                        conflicts.append(ReducibleFeature(7, 2, raw_conflict[0] - peripheral_neighbor, raw_conflict[1] | peripheral_neighbor))
                        continue
                 
                sys.stderr.write("\n[ReducibleFeature] The conflicting cubes {0} were not handled by any rule.".format(raw_conflicts))
                conflicts.append(ReducibleFeature(7, 0, raw_conflict[0], raw_conflict[1]))
                     
            return {"isolates": isolates, "conflicts": conflicts}
        
        def get_node_with_3_neighbors(node):
            neighbors = hypergraph.neighbors(node)
            assert len(neighbors) == 3
            return node, neighbors
        nodes_with_3_neighbors = map(get_node_with_3_neighbors, hypergraph.nodes_with_3_neighbors)
        
        triangles = get_triangles(nodes_with_3_neighbors)
        triangle_conflicts = get_triangle_conflicts(triangles)
        if triangle_conflicts["isolates"]:
            return triangle_conflicts["isolates"]
        
        buddies = list(get_buddies(nodes_with_3_neighbors))
        buddy_conflicts = get_buddy_conflicts(buddies)
        if buddy_conflicts["isolates"]:
            return buddy_conflicts["isolates"]
        
        cubes = list(get_cubes(nodes_with_3_neighbors))
        cube_conflicts = get_cube_conflicts(cubes)
        if cube_conflicts["isolates"]:
            return cube_conflicts["isolates"]
        
        if triangle_conflicts["conflicts"]:
            return triangle_conflicts["conflicts"]
        elif buddy_conflicts["conflicts"]:
            return buddy_conflicts["conflicts"]
        elif cube_conflicts["conflicts"]:
            return cube_conflicts["conflicts"]
        else:       
            return []
    
    @staticmethod
    def basic_degree_3_reduction(hypergraph, reducible, separator, perms, label_template, compute_string=True):
        return ReducibleFeature.degree_3_reduction(hypergraph, [reducible], separator, perms, label_template, compute_string)
    
    @staticmethod
    def degree_3_reduction(hypergraph, reducibles, separator, perms=None, label_template=None, compute_string=True):
        assert len(separator) <= 3
        if compute_string:
            assert perms
            assert label_template
        
        reducible_edges = map(lambda reducible: hypergraph.edges(reducible), reducibles)
        reducible_edges = set(itertools.chain(*reducible_edges))
        
        if compute_string:
            reducibles_labels = map(lambda reducible: hypergraph.node[reducible]["labels"][0], reducibles)
            possible_labels = []
            
            for perm in perms:
                possible_label = {}
                # TODO: we remove the reducible nodes from the direction of the new edge
                # However, this causes a change in the positions in the permutation.
                # How should this be handled?
                possible_label["perm"] = tuple(filter(lambda node: node not in reducibles, perm))
                possible_label["label"] = list(reducibles_labels)
                for edge in reducible_edges:
                    possible_label["label"].append(Hypergraph.edge_to_string(hypergraph, edge, perm))
                possible_label["label"] = ",".join(sorted(possible_label["label"]))
                possible_labels.append(possible_label)
            
            possible_labels = sorted(possible_labels, key=lambda element: element["label"])
            minimal_label = possible_labels[0]["label"]
            minimal_perm_indices = filter(lambda i: possible_labels[i]["label"] == minimal_label, range(len(possible_labels)))
            direction = set([possible_labels[i]["perm"] for i in minimal_perm_indices])
        else:
            direction = [] # TODO: an empty direction may cause problems
        
        hypergraph.remove_edges_from(reducible_edges, unsafe=True)
        if len(separator) > 0:
            hypergraph.remove_nodes_from(reducibles)
            if len(separator) > 1:
                new_edge_label = label_template.format(minimal_label) if compute_string else u""
                new_edge = hypergraph.add_edge(separator, direction, new_edge_label)
                return set([new_edge])
            else:
                if compute_string:
                    hypergraph.add_node_label(list(separator)[0], label_template.format(minimal_label))
                return set()
        else:
            not_reduced = list(reducibles)[0]
            hypergraph.remove_nodes_from(reducibles - set([not_reduced]))
            new_node_label = label_template.format(minimal_label) if compute_string else u""
            hypergraph.set_node_labels(not_reduced, [new_node_label])
            return set()
    
    # public methods
    
    def reduce(self, hypergraph, compute_string=True):
        if self.rule == 1:
            new_edges = set()
            self._reduce_by_rule_1(hypergraph, compute_string)
        elif self.rule == 2:
            new_edges = self._reduce_by_rule_2(hypergraph, compute_string)
        elif self.rule == 4:
            new_edges = self._reduce_by_rule_4(hypergraph, compute_string)
        elif self.rule == 5:
            new_edges = self._reduce_by_rule_5(hypergraph, compute_string)
        elif self.rule == 6:
            new_edges = self._reduce_by_rule_6(hypergraph, compute_string)
        elif self.rule == 7:
            new_edges = self._reduce_by_rule_7(hypergraph, compute_string)
        else:
            sys.stderr.write("\n[ReducibleFeature] Error: Unknown rule " + str(self.rule) + ".")
            return set()
        
        self.reduced = True
        
        return new_edges
    
    def as_subgraph(self, hypergraph):
        nodes = set(self.reducible_nodes) | set(self.peripheral_nodes)
        return hypergraph.subgraph_with_labels(nodes)
    
    def number_of_nodes(self):
        return len(self.reducible_nodes) + len(self.peripheral_nodes)
    
    def get_full_rule(self):
        return "{0}.{1}.{2}.{3}".format(self.rule, self.subrule, self.subsubrule, self.subsubsubrule)
    
    def __repr__(self, *args, **kwargs):
        reducible = u", ".join(map(lambda node: unicode(node), self.reducible_nodes))
        periphery = u", ".join(map(lambda node: unicode(node), self.peripheral_nodes))
        return u"rule({0}), [{1}]---[{2}]".format(self.get_full_rule(), reducible, periphery)
    
    def to_constructor_str(self):
        return u"ReducibleFeature({0}, {1}, {2}, {3}, {4}, {5})".format(
            self.rule,
            self.subrule,
            self.reducible_nodes,
            self.peripheral_nodes,
            self.subsubrule,
            self.subsubsubrule
        )
    
    # private methods
    
    def _reduce_by_rule_1(self, hypergraph, compute_string=True):
        if len(self.peripheral_nodes) != 1:
            sys.stderr.write("\n[ReducibleFeature] Error: The feature is not reducible by rule 1.")
        else:
            node = self.reducible_nodes[0]
            neighbor = self.peripheral_nodes[0]
            
            # dipole to single node
            if self.subrule == 1:
                if compute_string:
                    label_node_1 = hypergraph.node[node]["labels"][0]
                    label_node_2 = hypergraph.node[neighbor]["labels"][0]
                    
                    edge_id = hypergraph.edges(node, neighbor)[0]
                    
                    edge_label_1 = Hypergraph.edge_to_string(hypergraph, edge_id, (node, neighbor))
                    edge_label_2 = Hypergraph.edge_to_string(hypergraph, edge_id, (neighbor, node))
                    
                    label_template = u"(1.1;{0},{1},{2})"
                    label_1 = label_template.format(label_node_1, edge_label_1, label_node_2)
                    label_2 = label_template.format(label_node_2, edge_label_2, label_node_1)  
                    
                    label = ""
                    if cmp(label_1, label_2) <= 0:
                        label = label_1
                    else:
                        label = label_2              
                                    
                    hypergraph.set_node_labels(neighbor, [label])
                hypergraph.remove_node(node)
            # remove degree 1 leaves (pendant)
            elif self.subrule == 2:  
                if compute_string:         
                    edge_id = hypergraph.edges(node, neighbor)[0]
                    edge_label = Hypergraph.edge_to_string(hypergraph, edge_id, (neighbor, node))
                    
                    label = u"(1.2;{0},{1})".format(edge_label, hypergraph.node[node]["labels"][0])
                    hypergraph.add_node_label(neighbor, label)
                hypergraph.remove_node(node)
            else:
                sys.stderr.write("\n[ReducibleFeature] Error: Unknown subrule %d for rule 1." % self.subrule)
        
        return set()
    
    def _reduce_by_rule_2(self, hypergraph, compute_string=True):
        # chain
        if self.subrule == 1:
            if compute_string:
                s = self.peripheral_nodes[0]
                t = self.peripheral_nodes[1]
                path = [s] + self.reducible_nodes + [t]
                
                checked_hedges = set()
                
                labels_s_to_t = []
                labels_t_to_s = []
                for i in range(1, len(path)):
                    u = path[i - 1]
                    v = path[i]
                    
                    edges = hypergraph.edges(u, v)
                    new_labels_s_to_t = []
                    new_labels_t_to_s = []
                    for edge_id in edges:
                        if edge_id.startswith(u"he_"):
                            if edge_id in checked_hedges:
                                continue
                            w = path[i + 1]
                            new_labels_s_to_t.append(Hypergraph.edge_to_string(hypergraph, edge_id, (u, v, w)))
                            new_labels_t_to_s.append(Hypergraph.edge_to_string(hypergraph, edge_id, (w, v, u)))
                            checked_hedges.add(edge_id)
                        else:
                            new_labels_s_to_t.append(Hypergraph.edge_to_string(hypergraph, edge_id, (u, v)))
                            new_labels_t_to_s.append(Hypergraph.edge_to_string(hypergraph, edge_id, (v, u)))
                    labels_s_to_t += sorted(new_labels_s_to_t)
                    labels_t_to_s += sorted(new_labels_t_to_s)
                    
                    if i < len(path) - 1:
                        node_label = hypergraph.node[path[i]]["labels"][0]
                        labels_s_to_t.append(node_label)
                        labels_t_to_s.append(node_label)
                
                labels_t_to_s.reverse()
                
                label_template = u"(2.1;{0})"
                label_s_to_t = label_template.format(",".join(labels_s_to_t))
                label_t_to_s = label_template.format(",".join(labels_t_to_s))
                
                comparison = cmp(label_s_to_t, label_t_to_s)
                if comparison < 0:
                    new_edge = hypergraph.add_edge(self.peripheral_nodes, direction=[(s, t)], label=label_s_to_t)
                elif comparison > 0:
                    new_edge = hypergraph.add_edge(self.peripheral_nodes, direction=[(t, s)], label=label_t_to_s)
                else:
                    new_edge = hypergraph.add_edge(self.peripheral_nodes, label=label_s_to_t)
            else:
                new_edge = hypergraph.add_edge(self.peripheral_nodes, label="")
            
            hypergraph.remove_nodes_from(self.reducible_nodes)
            
            return set([new_edge])
        # ring
        elif self.subrule == 2:
            if compute_string:
                cycle = self.peripheral_nodes + self.reducible_nodes
                m = len(cycle)
                label_template = u"(2.2;{0})"
                possible_labels = []
                for i in range(0, m):
                    for k in [1, -1]:
                        label_components = []
                        checked_hedges = set()
                        for j in range(0, m):
                            index = i + k * j
                            u = cycle[index % m]
                            v = cycle[(index + k) % m]
                            
                            edge_ids = hypergraph.edges(u, v)
                            edge_labels = []
                            for edge_id in edge_ids:
                                if edge_id.startswith(u"he_"):
                                    if edge_id in checked_hedges:
                                        continue
                                    w = cycle[(index + 2 * k) % m]
                                    edge_labels.append(Hypergraph.edge_to_string(hypergraph, edge_id, (u, v, w)))
                                    checked_hedges.add(edge_id)
                                else:
                                    edge_labels.append(Hypergraph.edge_to_string(hypergraph, edge_id, (u, v)))
                            
                            label_components.append(hypergraph.node[u]["labels"][0])
                            label_components += sorted(edge_labels)
                        possible_labels.append(label_template.format(u",".join(label_components)))
                
                possible_labels.sort()
                hypergraph.set_node_labels(self.peripheral_nodes[0], [possible_labels[0]])
            hypergraph.remove_nodes_from(self.reducible_nodes)
            return set()
        else:
            sys.stderr.write("\n[ReducibleFeature] Error: Unknown subrule %d for rule 2." % self.subrule)
            return set()
    
    def _reduce_by_rule_4(self, hypergraph, compute_string=True):
        new_edges = set()
        if self.subrule == 1:
            # triangle
            if compute_string:
                label_template = u"(4.1;{0})"
                perms = permutations(self.peripheral_nodes)
                perms = map(lambda perm: perm + tuple([self.reducible_nodes[0]]), perms)
            else:
                perms = None
                label_template = None
            _new_edges = ReducibleFeature.basic_degree_3_reduction(hypergraph, self.reducible_nodes[0], self.peripheral_nodes, perms, label_template, compute_string)
            new_edges |= _new_edges
        elif self.subrule == 2:
            # buddy
            if compute_string:
                label_template = u"(4.2;{0})"
                perms = list(permutations(self.peripheral_nodes))
            else:
                label_template = None
            for reducible in self.reducible_nodes:
                if compute_string:
                    current_perms = map(lambda perm: perm + tuple([reducible]), perms)
                else:
                    current_perms = None
                _new_edges = ReducibleFeature.basic_degree_3_reduction(hypergraph, reducible, self.peripheral_nodes, current_perms, label_template, compute_string)
                new_edges |= _new_edges
        elif self.subrule == 3:
            # cube
            # TODO: the hub is not reduced in this step but in the next steps as a triangle-reducible vertex (in case it has degree 3)
            label_template = u"(4.3;{0})"
            for reducible in self.reducible_nodes:
                separator = hypergraph.neighbors(reducible)
                if compute_string:
                    perms = permutations(separator)
                    perms = map(lambda perm: perm + tuple([reducible]), perms)
                else:
                    perms = None
                _new_edges = ReducibleFeature.basic_degree_3_reduction(hypergraph, reducible, separator, perms, label_template, compute_string)
                new_edges |= _new_edges
        else:
            sys.stderr.write("\n[ReducibleFeature] Error: Unknown subrule %d for rule 4." % self.subrule)
        
        return new_edges
    
    def _reduce_by_rule_5(self, hypergraph, compute_string=True):
        new_edges = set()
        if self.subrule == 1:
            # diamonds
            if self.subsubrule == 1:
                # K4
                if compute_string:
                    label_template = u"(5.1.1;{0})"
                    perms = permutations(self.reducible_nodes | self.peripheral_nodes)
                else:
                    perms = None
                    label_template = None
                _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
                new_edges |= _new_edges
            elif self.subsubrule == 2:
                # K4-
                if compute_string:
                    label_template = u"(5.1.2;{0})"
                    s1, s2 = tuple(self.peripheral_nodes)
                    v1, v2 = tuple(self.reducible_nodes)
                    perms = [(s1, s2, v1, v2),
                             (s1, s2, v2, v1),
                             (s2, s1, v1, v2),
                             (s2, s1, v2, v1)]
                else:
                    perms = None
                    label_template = None
                _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
                new_edges |= _new_edges
            else:
                sys.stderr.write("\n[ReducibleFeature] Error: Unknown subsubrule %d for subrule 5.1." % self.subsubrule)
        elif self.subrule == 2:
            if self.subsubrule == 1:
                assert len(self.reducible_nodes) == 2
                assert len(self.peripheral_nodes) == 3
                if compute_string:
                    label_template = u"(5.2.1;{0})"
                    # TODO: nothing is mentioned about the permutations?
                    perms = permutations(self.reducible_nodes | self.peripheral_nodes)
                else:
                    perms = None
                    label_template = None
                _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
                new_edges |= _new_edges
            elif self.subsubrule == 2:
                label_template = u"(5.2.2;{0})"
                reducible_subgraph = hypergraph.subgraph(self.reducible_nodes)
                degree_1_nodes = filter(lambda node: reducible_subgraph.degree(node) == 1, self.reducible_nodes)
                degree_1_nodes_with_neighbors = [(node, hypergraph.neighbors(node)) for node in degree_1_nodes]
                for node_with_neighbors in degree_1_nodes_with_neighbors:
                    reducible = node_with_neighbors[0]
                    separator = node_with_neighbors[1]
                    if compute_string:
                        perms = permutations(separator)
                        perms = map(lambda perm: perm + tuple([reducible]), perms)
                    else:
                        perms = None
                    _new_edges = ReducibleFeature.basic_degree_3_reduction(hypergraph, reducible, separator, perms, label_template, compute_string)
                    new_edges |= _new_edges
            elif self.subsubrule == 3:
                if self.subsubsubrule == 1:
                    # wheel
                    assert len(self.reducible_nodes) == 3 or len(self.peripheral_nodes) == 1
                    def get_wheel_permutations():
                        preipheral_perms = list(permutations(self.peripheral_nodes))
                        ring_subgraph = hypergraph.subgraph(self.reducible_nodes)
                        ring = nx.cycle_basis(ring_subgraph)[0]
                        n = len(ring)
                        for i in range(n):
                            for preipheral_perm in preipheral_perms:
                                yield tuple(preipheral_perm) + tuple([ring[(i + j) % n] for j in range(n)])
                                yield tuple(preipheral_perm) + tuple([ring[(i - j) % n] for j in range(n)])
                    if compute_string:
                        label_template = u"(5.2.3.1;{0})"
                        # TODO: nothing is mentioned about the permutations?
                        perms = get_wheel_permutations()
                    else:
                        perms = None
                        label_template = None
                    _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
                    new_edges |= _new_edges
                elif self.subsubsubrule == 2:
#                     # TODO: this reduction is not correct for all cases
#                     assert len(self.peripheral_nodes) <= 3
#                     if compute_string:
#                         label_template = u"(5.2.3.2;{0})"
#                         perms = permutations(self.reducible_nodes | self.peripheral_nodes)
#                     else:
#                         perms = None
#                         label_template = None
#                     _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
#                     new_edges |= _new_edges
                    sys.stderr.write("\n[ReducibleFeature] Error: There is not reduction available for rule 5.2.3.2 because this rule disassembles the features into sub-features of different rules.")
                elif self.subsubsubrule == 3:
                    # square
                    assert len(self.reducible_nodes) == 4
                    assert len(self.peripheral_nodes) == 2
                    if compute_string:
                        label_template = u"(5.2.3.3;{0})"
                        # TODO: nothing is mentioned about the permutations?
                        perms = permutations(self.reducible_nodes | self.peripheral_nodes)
                    else:
                        perms = None
                        label_template = None
                    _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
                    new_edges |= _new_edges
                else:
                    sys.stderr.write("\n[ReducibleFeature] Error: Unknown subsubsubrule %d for subsubrule 5.2.3." % self.subsubsubrule)
            elif self.subsubrule == 4:
                label_template = u"(5.2.4;{0})"
                reducible_subgraph = hypergraph.subgraph(self.reducible_nodes)
                degree_2_nodes = filter(lambda node: reducible_subgraph.degree(node) == 2, self.reducible_nodes)
                cc = nx.connected_components(reducible_subgraph.subgraph(degree_2_nodes))
                for comp in cc:
                    if len(comp) == 2:
                        reducibles = list(comp)
                        separator = (set(hypergraph.neighbors(reducibles[0])) | set(hypergraph.neighbors(reducibles[1]))) - comp
                        if compute_string:
                            # TODO: nothing is mentioned about the permutations?
                            perms = permutations(comp | separator)
                        else:
                            perms = None
                        _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, reducibles, separator, perms, label_template, compute_string)
                        new_edges |= _new_edges
                    else:
                        comp_subgraph = reducible_subgraph.subgraph(comp)
                        degree_1_nodes = filter(lambda node: comp_subgraph.degree(node) <= 1, comp)
                        for reducible in degree_1_nodes:
                            separator = hypergraph.neighbors(reducible)
                            if compute_string:
                                perms = permutations(separator)
                                perms = map(lambda perm: perm + tuple([reducible]), perms)
                            else:
                                perms = None
                            _new_edges = ReducibleFeature.basic_degree_3_reduction(hypergraph, reducible, separator, perms, label_template, compute_string)
                            new_edges |= _new_edges
            elif self.subsubrule == 5:
                # prism
                assert len(self.peripheral_nodes) == 0
                if compute_string:
                    label_template = u"(5.2.5;{0})"
                    # TODO: nothing is mentioned about the permutations?
                    perms = permutations(self.reducible_nodes)
                else:
                    perms = None
                    label_template = None
                _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
                new_edges |= _new_edges
            else:
                sys.stderr.write("\n[ReducibleFeature] Error: Unknown subsubrule %d for subrule 5.2." % self.subsubrule)
        else:
            sys.stderr.write("\n[ReducibleFeature] Error: Unknown subrule %d for rule 5." % self.subrule)
        
        return new_edges
    
    def _reduce_by_rule_6(self, hypergraph, compute_string=True):
        new_edges = set()
        if self.subrule == 1:
            # K(3,3)
            if compute_string:
                label_template = u"(6.1;{0})"
                # TODO: nothing is mentioned about the permutations?
                perms = permutations(self.reducible_nodes | self.peripheral_nodes)
            else:
                perms = None
                label_template = None
            _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
            new_edges |= _new_edges
        elif self.subrule == 2:
            # Cat's cradle
            assert len(self.reducible_nodes) == 4
            assert len(self.peripheral_nodes) == 2
            if compute_string:
                label_template = u"(6.2;{0})"
                # TODO: nothing is mentioned about the permutations?
                red_perms = list(permutations(self.reducible_nodes))
                perms = map(lambda perm: tuple(self.peripheral_nodes) + perm, red_perms)
                perms += map(lambda perm: tuple(list(self.peripheral_nodes)[::-1]) + perm, red_perms)
            else:
                perms = None
                label_template = None
            _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
            new_edges |= _new_edges
        else:
            sys.stderr.write("\n[ReducibleFeature] Error: Unknown subrule %d for rule 6." % self.subrule)
        
        return new_edges
    
    def _reduce_by_rule_7(self, hypergraph, compute_string=True):
        new_edges = set()
        if self.subrule == 1:
            # cube
            assert len(self.reducible_nodes) == 8
            assert len(self.peripheral_nodes) == 0
            if compute_string:
                label_template = u"(7.1;{0})"
                # TODO: nothing is mentioned about the permutations?
                perms = permutations(self.reducible_nodes)
            else:
                perms = None
                label_template = None
            _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
            new_edges |= _new_edges
        elif self.subrule == 2:
            # Hammock
            assert len(self.reducible_nodes) == 6
            assert len(self.peripheral_nodes) == 2
            if compute_string:
                label_template = u"(7.2;{0})"
                # TODO: nothing is mentioned about the permutations?
                red_perms = list(permutations(self.reducible_nodes))
                perms = map(lambda perm: tuple(self.peripheral_nodes) + perm, red_perms)
                perms += map(lambda perm: tuple(list(self.peripheral_nodes)[::-1]) + perm, red_perms)
            else:
                perms = None
                label_template = None
            _new_edges = ReducibleFeature.degree_3_reduction(hypergraph, self.reducible_nodes, self.peripheral_nodes, perms, label_template, compute_string)
            new_edges |= _new_edges
        else:
            sys.stderr.write("\n[ReducibleFeature] Error: Unknown subrule %d for rule 7." % self.subrule)
        
        return new_edges
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            self_dict = dict(self.__dict__)
            other_dict = dict(other.__dict__)
            del self_dict["reduced"]
            del other_dict["reduced"]
            return self_dict == other_dict
        else:
            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __init__(self, rule, subrule, reducible_nodes, peripheral_nodes, subsubrule = 0, subsubsubrule = 0):
        '''Constructor
        
        Rule meanings
        -------------
        rule 0: Multiple vertices and edges (implemented in class ArnborgProskurowski)
        rule 1: Pendant rule
            subrule 1: Dipole
            subrule 2: Pendant vertices
            subrule 3: Self-loops (implemented in class ArnborgProskurowski)
        rule 2: Series rule
            subrule 1: Chain
            subrule 2: Ring
        rule 3: TODO
        '''
        self.rule = rule
        self.subrule = subrule
        self.subsubrule = subsubrule
        self.subsubsubrule = subsubsubrule
        self.reduced = False
        self.reducible_nodes = reducible_nodes
        self.peripheral_nodes = peripheral_nodes
