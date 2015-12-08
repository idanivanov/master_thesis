'''
Created on Nov 24, 2015

@author: Ivan Ivanov
'''
import codecs
import itertools

'''
From a file containing treewidths of graphs, get the number of graphs grouped by treewidth.

@param tw_file: CSV file containing treewidths in the following format: each line represents a tuple "graph_id,treewidth"
@return: Dictionary of the format { treewidth: graphs_count }
'''
def aggregate(tw_file_path):
    lines = read_tw_file(tw_file_path)
    res = {}
    for k, g in itertools.groupby(lines, lambda tup: tup[1]):
        group_count = sum(1 for _ in g)
        if res.has_key(k):
            res[k] += group_count
        else:
            res[k] = group_count
    res["total"] = sum(res.values())
    return res
    

def read_tw_file(tw_file_path):
    tw_file = codecs.open(tw_file_path, "r", "utf8")
    line = tw_file.readline()
    while line:
        items = line[:-1].split(u",")
        if len(items) == 2:
            yield (items[0], items[1])
        line = tw_file.readline()
    tw_file.close()
