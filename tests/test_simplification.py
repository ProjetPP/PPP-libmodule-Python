import unittest

from ppp_datamodel.nodes import Triple as T
from ppp_datamodel.nodes import Missing as M
from ppp_datamodel.nodes import Resource as R
from ppp_datamodel.nodes.list_operators import *
from ppp_libmodule.simplification import simplify


class SimplificationTestCase(unittest.TestCase):
    def testUnionTrivial(self):
        self.assertEqual(simplify(Union([])), List([]))
        self.assertEqual(simplify(Union([List([R('a')])])),
                List([R('a')]))
    def testUnionResourceLists(self):
        t = Union([List([R('a'), R('b')]), List([R('c')])])
        t = simplify(t)
        self.assertIsInstance(t, List)
        self.assertEqual(set(t.list), {R('a'), R('b'), R('c')})
    def testUnionMixed(self):
        t = Union([List([R('a'), R('b')]), T(M(), M(), M())])
        t = simplify(t)
        self.assertIsInstance(t, Union)
        self.assertEqual(t.list[0], T(M(), M(), M()))
        self.assertIsInstance(t.list[1], List)
        self.assertEqual(set(t.list[1].list), {R('a'), R('b')})

    def testIntersectionTrivial(self):
        self.assertEqual(simplify(Intersection([])), Intersection([]))
        self.assertEqual(simplify(Intersection([List([R('a')])])),
                List([R('a')]))
    def testIntersectionResourceLists(self):
        t = Intersection([List([R('a'), R('b')]), List([R('c'), R('a')])])
        t = simplify(t)
        self.assertEqual(t, List([R('a')]))
    def testIntersectionMixed(self):
        t = Intersection([List([R('a'), R('b')]), List([R('c'), R('a')]),
                         T(M(), M(), M())])
        t = simplify(t)
        self.assertIsInstance(t, Intersection)
        self.assertEqual(t.list[0], T(M(), M(), M()))
        self.assertEqual(t.list[1], List([R('a')]))
