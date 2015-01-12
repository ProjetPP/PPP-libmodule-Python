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

    (lists, non_lists) = partition(lambda x:isinstance(x, List), tree.list)
    # Make union of lists
    lists = map(operator.attrgetter('list'), lists)
    lists = list(set(itertools.chain(*lists)))

    non_lists = list(non_lists)
    if non_lists: # If there are non-lists (eg. triples)
        all_ = non_lists
        all_.append(List(lists))
        return Union(all_)
    else: # If there are only lists
        return List(lists)

def simplify_intersection(tree):
    # Trivial cases
    if len(tree.list) == 0:
        return tree
    elif len(tree.list) == 1:
        return tree.list[0]

    (lists, non_lists) = partition(lambda x:isinstance(x, List), tree.list)
    # Make intersection of lists
    lists = list(map(set, map(operator.attrgetter('list'), lists)))
    lists = list(lists[0].intersection(*lists[1:]))

    non_lists = list(non_lists)
    if non_lists: # If there are non-lists (eg. triples)
        all_ = non_lists
        all_.append(List(lists))
        return Intersection(all_)
    else: # If there are only lists
        return List(lists)


predicates = {
        Union: simplify_union,
        Intersection: simplify_intersection,
        }

def predicate(tree):
    for (cls, f) in predicates.items():
        if isinstance(tree, cls):
            return f(tree)
    return tree

def simplify(tree):
    return tree.traverse(predicate)
