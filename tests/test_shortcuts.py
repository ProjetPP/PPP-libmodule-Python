from ppp_libmodule.tests import PPPTestCase
from ppp_libmodule.http import HttpRequestHandler
from ppp_libmodule import shortcuts

from ppp_datamodel.nodes import Triple as T
from ppp_datamodel.nodes import Missing as M
from ppp_datamodel.nodes import Missing as R
from ppp_datamodel.nodes import List as L
from ppp_datamodel.communication import Response, TraceItem

def predicate(node):
    if node == T(M(), M(), M()):
        return R('foo')
    elif node == R('foo'):
        return R('bar')
    elif node == M():
        return node
    elif node == L([]):
        return node
    else:
        assert False, node

class RequestHandler:
    def __init__(self, request):
        self.request = request

    def answer(self):
        tree = self.request.tree.traverse(predicate)
        if tree != self.request.tree:
            # If we have modified the tree, it is relevant to return it
            return [shortcuts.build_answer(self.request, tree, {}, 'test')]
        else:
            # Otherwise, we have nothing interesting to say.
            return []

def app(environ, start_response):
    """Function called by the WSGI server."""
    r = HttpRequestHandler(environ, start_response, RequestHandler).dispatch()
    return r

class HttpTest(PPPTestCase(app)):
    def testWorking(self):
        t = T(M(), M(), M())
        q = {'id': '1', 'language': 'en', 'tree': t.as_dict(),
              'measures': {}, 'trace': []}
        self.assertResponse(q, [Response('en', R('bar'), {},
            [TraceItem('test', R('bar'), {})])])

