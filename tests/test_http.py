"""Test HTTP capabilities of the core's frontend."""

from ppp_libmodule.tests import PPPTestCase
from ppp_libmodule.http import HttpRequestHandler

r = None

class RequestHandler:
    def __init__(self, request):
        global r
        r = request

    def answer(self):
        return []

def app(environ, start_response):
    """Function called by the WSGI server."""
    r = HttpRequestHandler(environ, start_response, RequestHandler).dispatch()
    return r

class HttpTest(PPPTestCase(app)):
    def testPostOnly(self):
        self.assertEqual(self.app.get('/', status='*').status_int, 405)
        self.assertEqual(self.app.put('/', status='*').status_int, 405)
    def testNotRoot(self):
        self.assertEqual(self.app.post_json('/foo', {}, status='*').status_int, 400)
    def testNotJson(self):
        self.assertEqual(self.app.post('/', 'foobar', status='*').status_int, 400)
    def testWorking(self):
        global r
        q = {'id': '1', 'language': 'en', 'tree': {'type': 'triple',
             'subject': {'type': 'resource', 'value': 'foo'},
             'predicate': {'type': 'resource', 'value': 'bar'},
             'object': {'type': 'resource', 'value': 'baz'}},
              'measures': {}, 'trace': []}
        r = None
        self.assertResponse(q, [])
        self.assertEqual(r.as_dict(), q)
    def testNoTree(self):
        q = {'language': 'en'}
        self.assertStatusInt(q, 400)
