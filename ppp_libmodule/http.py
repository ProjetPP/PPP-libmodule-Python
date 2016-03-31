"""Handles the HTTP frontend (ie. answers to requests from a
UI."""

import time
import json
import logging

from ppp_datamodel.exceptions import AttributeNotProvided
from ppp_datamodel.communication import Request

from .config import Config
from .exceptions import ClientError, BadGateway, InvalidConfig

DOC_URL = 'https://github.com/ProjetPP/Documentation/blob/master/' \
          'module-communication.md#frontend'

class HttpRequestHandler:
    """Handles one request."""
    def __init__(self, environ, start_response, router_class):
        self.environ = environ
        self.start_response = start_response
        self.router_class = router_class
    def make_response(self, status, content_type, response):
        """Shortcut for making a response to the client's request."""
        headers = [('Access-Control-Allow-Origin', '*'),
                   ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                   ('Access-Control-Allow-Headers', 'Content-Type'),
                   ('Access-Control-Max-Age', '86400'),
                   ('Content-type', content_type)
                  ]
        self.start_response(status, headers)
        return [response.encode()]

    def on_bad_method(self):
        """Returns a basic response to GET requests (probably sent by humans
        trying to open the link in a web browser."""
        text = 'Bad method, only POST is supported. See: ' + DOC_URL
        return self.make_response('405 Method Not Allowed',
                                  'text/plain',
                                  text
                                 )

    def on_unknown_uri(self):
        """Returns a basic response to GET requests (probably sent by humans
        trying to open the link in a web browser."""
        text = 'URI not found, only / is supported. See: ' + DOC_URL
        return self.make_response('404 Not Found',
                                  'text/plain',
                                  text
                                 )

    def on_bad_request(self, hint):
        """Returns a basic response to invalid requests."""
        return self.make_response('400 Bad Request',
                                  'text/plain',
                                  hint
                                 )

    def on_bad_gateway(self, exc):
        """Returns a basic response when a module is buggy."""
        return self.make_response('502 Bad Gateway',
                                  'text/plain',
                                  exc.args[0]
                                 )

    def on_client_error(self, exc):
        """Handler for any error in the request detected by the module."""
        return self.on_bad_request(exc.args[0])

    def on_internal_error(self): # pragma: no cover
        """Returns a basic response when the module crashed"""
        return self.make_response('500 Internal Server Error',
                                  'text/plain',
                                  'Internal server error. Sorry :/'
                                 )

    def _get_times(self):
        wall_time = time.time()
        get_process_time = getattr(time, 'process_time', None)
        if get_process_time: # Python ≥ 3.3 only
            process_time = get_process_time()
        else:
            process_time = None
        return (wall_time, process_time)

    def _add_times_to_answers(self, answers, start_wall_time, start_process_time):
        (end_wall_time, end_process_time) = self._get_times()
        times_dict = {'start': start_wall_time, 'end': end_wall_time}
        if start_wall_time and end_process_time:
            times_dict['cpu'] = end_process_time - start_process_time
        for answer in answers:
            if not answer.trace:
                continue
            if answer.trace[0].times == {}:
                answer.trace[0].times.update(times_dict)

    def process_request(self, request):
        """Processes a request."""
        try:
            request = Request.from_json(request.read().decode())
        except ValueError:
            raise ClientError('Data is not valid JSON.')
        except KeyError:
            raise ClientError('Missing mandatory field in request object.')
        except AttributeNotProvided as exc:
            raise ClientError('Attribute not provided: %s.' % exc.args[0])

        (start_wall_time, start_process_time) = self._get_times()
        answers = self.router_class(request).answer()
        self._add_times_to_answers(answers, start_wall_time, start_process_time)

        answers = [x.as_dict() for x in answers]
        return self.make_response('200 OK',
                                  'application/json',
                                  json.dumps(answers)
                                 )

    def on_post(self):
        """Extracts the request, feeds the module, and returns the response."""
        request = self.environ['wsgi.input']
        try:
            return self.process_request(request)
        except ClientError as exc:
            return self.on_client_error(exc)
        except BadGateway as exc:
            return self.on_bad_gateway(exc)
        except InvalidConfig:
            raise
        except Exception as exc: # pragma: no cover # pylint: disable=W0703
            logging.error('Unknown exception: ', exc_info=exc)
            return self.on_internal_error()

    def on_options(self):
        """Tells the client we allow requests from any Javascript script."""
        return self.make_response('200 OK', 'text/html', '')

    def dispatch(self):
        """Handles dispatching of the request."""
        method_name = 'on_' + self.environ['REQUEST_METHOD'].lower()
        method = getattr(self, method_name, None)
        if method:
            return method()
        else:
            return self.on_bad_method()

