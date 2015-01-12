import operator
import itertools

from ppp_datamodel.nodes import Resource
from ppp_datamodel.nodes.list_operators import *

__all__ = ['simplify']

def partition(pred, list_):
    # Partition the items in lists / non-lists
    list_ = [x for x in list_ if x]
    lists = filter(pred, list_)
    not_lists = itertools.filterfalse(pred, list_)
    return (lists, not_lists)

def simplify_union(tree):
    # Trivial cases
    if len(tree.list) == 0:
        return List([])
    elif len(tree.list) == 1:
        return tree.list[0]

    (lists, non_lists) = partition(lambda x:isinstance(x, (List, Resource)),
                                   tree.list)
    # Make union of lists
    lists = [x.list if isinstance(x, List) else [x] for x in lists]
    lists = list(set(itertools.chain(*lists)))

    non_lists = list(non_lists)
    if lists:
        all_ = non_lists
        all_.append(List(lists))
        return Union(all_)
    else:
        return List(non_lists)

def simplify_intersection(tree):
    # Trivial cases
    if len(tree.list) == 0:
        return tree
    elif len(tree.list) == 1:
        return tree.list[0]

    (a, b) = partition(lambda x:isinstance(x, (List, Resource)), tree.list)
    (lists, non_lists) = partition(lambda x:isinstance(x, (List, Resource)),
                                   tree.list)
    # Make intersection of lists
    lists = [set(x.list) if isinstance(x, List) else {x} for x in lists] or [set()]
    lists = list(lists[0].intersection(*lists[1:]))

    non_lists = list(non_lists)
    if lists:
        all_ = non_lists
        all_.append(simplify_list(List(lists)))
        return Intersection(all_)
    else:
        return List(non_lists)

def simplify_list(tree):
    if len(tree.list) == 1:
        return tree.list[0]
    else:
        return tree

predicates = {
        Union: simplify_union,
        Intersection: simplify_intersection,
        List: simplify_list,
        }

def predicate(tree):
    for (cls, f) in predicates.items():
        if isinstance(tree, cls):
            return f(tree)
    return tree

def simplify(tree):
    old_tree = None
    while old_tree != tree:
        old_tree = tree
        tree = tree.traverse(predicate)
    return tree
