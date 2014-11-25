"""Test framework for running tests of PPP modules."""

__all__ = ['PPPTestCase']

import os
import json
import tempfile
from webtest import TestApp
from unittest import TestCase
from ppp_datamodel.communication import Request, Response

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
                del os.environ[self.config.var]
                del self.config_file
            super(_PPPTestCase, self).tearDown()

        def request(self, obj):
            if isinstance(obj, Request):
                obj = obj.as_dict()
            elif isinstance(obj, str):
                obj = json.loads(obj)
            j = self.app.post_json('/', obj).json
            return list(map(Response.from_dict, j))
        def assertResponse(self, request, response):
            self.assertEqual(self.request(request), response)
        def assertResponsesIn(self, request, expected):
            responses = self.request(request)
            self.assertTrue(all(x in expected for x in responses),
                            'Not all of:\n%r\n are in:\n%r' % (responses, expected))
        def assertResponsesCount(self, request, count):
            self.assertEqual(len(self.request(request)), count)
        def assertStatusInt(self, request, status):
            res = self.app.post_json('/', request, status='*')
            self.assertEqual(res.status_int, status)
    return _PPPTestCase

