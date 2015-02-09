"""Test framework for running tests of PPP modules."""

__all__ = ['PPPTestCase']

import os
import json
import tempfile
from webtest import TestApp
from unittest import TestCase
from ppp_datamodel.communication import Request, Response

def arg_to_dict(f):
    """Converts the first argument to the function to a dict
    (assuming it's either a json-encoding string or a Request object)."""
    def newf(self, obj, *args, **kwargs):
        if isinstance(obj, Request):
            obj = obj.as_dict()
        elif isinstance(obj, str):
            obj = json.loads(obj)
        return f(self, obj, *args, **kwargs)
    return newf

def PPPTestCase(app):
    class _PPPTestCase(TestCase):
        config_var = None
        config = None
        def setUp(self):
            super(_PPPTestCase, self).setUp()
            self.app = TestApp(app)
            if self.config_var or self.config is not None:
                assert self.config_var and self.config is not None
                self.config_file = tempfile.NamedTemporaryFile('w+')
                os.environ[self.config_var] = self.config_file.name
                self.config_file.write(self.config)
                self.config_file.seek(0)
        def tearDown(self):
            if self.config_var or self.config is not None:
                assert self.config_var and self.config is not None
                self.config_file.close()
                del os.environ[self.config_var]
                del self.config_file
            super(_PPPTestCase, self).tearDown()

        @arg_to_dict
        def request(self, obj):
            j = self.app.post_json('/', obj).json
            """Make a request and return the answers."""
            return list(map(Response.from_dict, j))
        @arg_to_dict
        def assertResponse(self, request, response):
            """Makes a request and asserts the response is the expected one."""
            self.assertEqual(self.request(request), response)
        @arg_to_dict
        def assertResponsesIn(self, request, expected):
            """Makes a request and asserts the response is among a set
            of expected ones."""
            responses = self.request(request)
            self.assertTrue(all(x in expected for x in responses),
                            'Not all of:\n%r\n are in:\n%r' % (responses, expected))
        @arg_to_dict
        def assertResponsesCount(self, request, count):
            """Makes a request and asserts the number of responses is
            a given number."""
            self.assertEqual(len(self.request(request)), count)
        @arg_to_dict
        def assertStatusInt(self, obj, status):
            """Makes a request and asserts the HTTP status code is
            the one that is expected."""
            res = self.app.post_json('/', obj, status='*')
            self.assertEqual(res.status_int, status)
    return _PPPTestCase

