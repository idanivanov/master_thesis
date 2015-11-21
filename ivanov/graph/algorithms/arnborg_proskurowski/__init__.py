'''
Created on Nov 21, 2015

@author: Ivan Ivanov
'''

from reducible_feature import ReducibleFeature
from ivanov.graph.hypergraph import Hypergraph
from itertools import groupby, permutations
import sys
 
def get_canonical_representation(graph, return_features = False):
    
    def get_features_strings(features):
        features_strings = []
        for feature in features:
            # TODO: this subgraph extraction is weird
            subgraph = feature.as_subgraph(graph)
            canon_str = get_canonical_representation(subgraph)
            feature_string = u"{0}.{1};{2}".format(feature.rule, feature.subrule, canon_str)
            features_strings.append(feature_string)
        return features_strings
    
    def is_done(hypergraph):
        if hypergraph.number_of_edges() == 0:
            return True
        else:
            return False
    
    def collect_labels(hypergraph):
        labels = []
        
        for node in hypergraph.nodes_iter():
            labels.append(hypergraph.node[node]["labels"][0])
        
        labels.sort()
        
        return u",".join(labels)
    
    def rule_0(hypergraph):
        modified = False
        
        # rule 0.1
        nodes_with_more_labels = filter(lambda node: len(hypergraph.node[node]["labels"]) > 1, hypergraph.nodes_iter())
        if len(nodes_with_more_labels) > 0:
            modified = True
            
        for node in nodes_with_more_labels:
            labels = hypergraph.node[node]["labels"]
            labels.sort()
            new_label = u"(0.1;{0})".format(u",".join(labels))
            hypergraph.node[node]["labels"] = [new_label]
        
        # rule 0.2
        edges_endpoints = map(lambda edge: (edge, u",".join(sorted(hypergraph.endpoints(edge)))), hypergraph.edges_2_iter())
        edges_endpoints.sort(key=lambda e: e[1])
        edges_grouped_by_neighbors = groupby(edges_endpoints, key=lambda e: e[1])
        edges_groups = map(lambda key_group: [elem[0] for elem in key_group[1]], edges_grouped_by_neighbors)
        parallel_edge_groups = filter(lambda group: len(group) > 1, edges_groups)
        
        if len(parallel_edge_groups) > 0:
            modified = True
        
        for edge_group in parallel_edge_groups:
            endpoints = hypergraph.endpoints(edge_group[0])
            perms = permutations(endpoints)
            possible_labels = []
            for perm in perms:
                possible_label = {}
                possible_label["perm"] = perm
                possible_label["label"] = []
                for edge in edge_group:
                    possible_label["label"].append(Hypergraph.edge_to_string(hypergraph, edge, perm))
                possible_label["label"].sort()
                possible_label["label"] = u"(0.2;{0})".format(u",".join(possible_label["label"]))
                possible_labels.append(possible_label)
            possible_labels = sorted(possible_labels, key=lambda element: element["label"])
            minimal_label = possible_labels[0]["label"]
            minimal_perm_indices = filter(lambda i: possible_labels[i]["label"] == minimal_label, range(len(possible_labels)))
            direction = set([possible_labels[i]["perm"] for i in minimal_perm_indices])
            hypergraph.remove_edges_from(edge_group)
            hypergraph.add_edge(endpoints, direction, minimal_label)
        
        return modified
        
    def rule_1(hypergraph, return_features = False):
        modified = False
        pendant_features = ReducibleFeature.extract_rule_1_features(hypergraph)
        
        for feature in pendant_features:
            if not modified:
                modified = True
            feature.reduce(hypergraph)
        
        # 1.3 - remove self-loops
        self_loops = hypergraph.self_loops()
        for self_loop in self_loops:
            if not modified:
                modified = True
            node = hypergraph.endpoints(self_loop)[0]
            hypergraph.node[node]["labels"].append(hypergraph.edge(self_loop)["labels"][0])
            hypergraph.remove_edge(self_loop)
        
        return modified, pendant_features if return_features else None
    
    def rule_2(hypergraph, return_features = False):
        modified = False
        series_features = ReducibleFeature.extract_rule_2_features(hypergraph)
        
        for feature in series_features:
            if not modified:
                modified = True
            feature.reduce(hypergraph)
        
        return modified, series_features if return_features else None
    
    def rule_3(hypergraph):
        modified = False
        
        all_hedges = hypergraph.hedges_iter()
        hedges_endpoints = map(lambda hedge: (hedge, u",".join(sorted(hypergraph.endpoints(hedge)))), all_hedges)
        hedges_endpoints.sort(key=lambda h: h[1])
        hedges_grouped_by_neighbors = groupby(hedges_endpoints, key=lambda h: h[1])
        hedges_groups = map(lambda key_group: [elem[0] for elem in key_group[1]], hedges_grouped_by_neighbors)
        parallel_hedge_groups = filter(lambda group: len(group) > 1, hedges_groups)
        
        if len(parallel_hedge_groups) > 0:
            modified = True
        
        for hedge_group in parallel_hedge_groups:
            endpoints = hypergraph.endpoints(hedge_group[0])
            perms = permutations(endpoints)
            possible_labels = []
            for perm in perms:
                possible_label = {}
                possible_label["perm"] = perm
                possible_label["label"] = []
                for hedge in hedge_group:
                    possible_label["label"].append(Hypergraph.hedge_to_string(hypergraph, hedge, perm))
                possible_label["label"].sort()
                possible_label["label"] = u",".join(possible_label["label"])
                possible_labels.append(possible_label)
            possible_labels = sorted(possible_labels, key=lambda element: element["label"])
            minimal_label = possible_labels[0]["label"]
            minimal_perm_indices = filter(lambda i: possible_labels[i]["label"] == minimal_label, range(len(possible_labels)))
            direction = set([possible_labels[i]["perm"] for i in minimal_perm_indices])
            hypergraph.remove_edges_from(hedge_group)
            hypergraph.add_edge(endpoints, direction, u"(3;{0})".format(minimal_label))
        
        return modified
    
    def rules_4_5_6_7(hypergraph, return_features = False):
        modified = False
        degree_3_features = ReducibleFeature.extract_degree_3_features(hypergraph)
        
        for feature in degree_3_features:
            if not modified:
                modified = True
            feature.reduce(hypergraph)
        
        return modified, degree_3_features if return_features else None
    
    hypergraph = Hypergraph(graph)
    features = []
    treewidth = 0
    
    if hypergraph.number_of_nodes() == 0:
        if return_features:
            return treewidth, "", features
        else:
            return treewidth, ""
    
    new_features = []
            
    while True:
        modified = False
        
        if return_features:
            features.append(get_features_strings(new_features))
        
#         if hypergraph.number_of_nodes() < 50: 
#             hypergraph.visualize()
        
        modified = rule_0(hypergraph)
        if modified:
            new_features = []
            continue
        
        modified, new_features = rule_1(hypergraph, return_features)
        if modified:
            if treewidth < 1:
                treewidth = 1
            continue
        
        modified, new_features = rule_2(hypergraph, return_features)
        if modified:
            if treewidth < 2:
                treewidth = 2
            continue
        
        modified = rule_3(hypergraph)
        if modified:
            new_features = []
            continue
         
        modified, new_features = rules_4_5_6_7(hypergraph, return_features)
        if modified:
            if treewidth < 3:
                treewidth = 3
            continue
        else:
            if is_done(hypergraph):
                if hypergraph.number_of_nodes() == 0:
                    sys.stderr.write("\n[ArnborgProskurowski] Error: empty graph produced.")
                    if return_features:
                        return treewidth, u"", features
                    else:
                        return treewidth, u""
                else:
                    canon_str = collect_labels(hypergraph)
                    if return_features:
                        features.append(get_features_strings(new_features))
                        return treewidth, canon_str, features
                    else:
                        return treewidth, canon_str
            else:
                if return_features:
                    features.append(get_features_strings(new_features))
                    return -1, u"Tree-width > 3", features
                else:
                    return -1, u"Tree-width > 3"
