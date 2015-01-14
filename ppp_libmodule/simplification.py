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
    elif len(non_lists) == 1:
        return non_lists
    else:
        return Union(non_lists)

def simplify_intersection(tree):
    # Trivial cases
    if len(tree.list) == 0:
        return tree
    elif len(tree.list) == 1:
        return tree.list[0]

    (a, b) = partition(lambda x:isinstance(x, (List, Resource)), tree.list)
    (lists, non_lists) = partition(lambda x:isinstance(x, (List, Resource)),
                                   tree.list)
    lists = list(lists)
    # Make intersection of lists
    try:
        # Efficient algorithm if everything is hashable
        lists = [set(x.list) if isinstance(x, List) else {x} for x in lists] or [set()]
        lists = list(lists[0].intersection(*lists[1:]))
    except TypeError:
        # If there is a non-hashable value, fallback to a less efficient algorithm
        lists = [x.list if isinstance(x, List) else [x] for x in lists] or [[]]
        intersected_lists = list(lists[0])
        for l in lists[1:]:
            intersected_lists = [x for x in intersected_lists if x in l]
        lists = intersected_lists

    non_lists = list(non_lists)
    if lists:
        all_ = non_lists
        all_.append(simplify_list(List(lists)))
        return Intersection(all_)
    elif len(non_lists) == 1:
        return non_lists
    else:
        return Intersection(non_lists)

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
