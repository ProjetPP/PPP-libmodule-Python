import itertools

from ppp_datamodel.nodes import Resource
from ppp_datamodel.nodes.list_operators import *

__all__ = ['simplify']

def simplify_union(tree):
    if len(tree.list) == 0:
        return List([])
    elif len(tree.list) == 1:
        return tree.list[0]
    list_ = [x for x in tree.list if x]
    lists = (x.list for x in list_ if isinstance(x, List))
    not_lists = [x for x in list_ if not isinstance(x, List)]
    lists = list(set(itertools.chain(*lists)))
    if not_lists:
        all_ = not_lists
        all_.append(List(lists))
        return Union(all_)
    else:
        return List(lists)


predicates = {
        Union: simplify_union
        }

def predicate(tree):
    for (cls, f) in predicates.items():
        if isinstance(tree, cls):
            return f(tree)
    return tree

def simplify(tree):
    return tree.traverse(predicate)
