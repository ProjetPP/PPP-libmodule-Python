# PPP libmodule-Python application.

[![Build Status](https://scrutinizer-ci.com/g/ProjetPP/PPP-libmodule-Python/badges/build.png?b=master)](https://scrutinizer-ci.com/g/ProjetPP/PPP-libmodule-Python/build-status/master)
[![Code Coverage](https://scrutinizer-ci.com/g/ProjetPP/PPP-libmodule-Python/badges/coverage.png?b=master)](https://scrutinizer-ci.com/g/ProjetPP/PPP-libmodule-Python/?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/ProjetPP/PPP-libmodule-Python/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/ProjetPP/PPP-libmodule-Python/?branch=master)


# How to install

With a recent version of pip:

```
pip3 install git+https://github.com/ProjetPP/PPP-libmodule-Python.git
```

With an older one:

```
git clone https://github.com/ProjetPP/PPP-libmodule-Python.git
cd PPP-libmodule-Python
python3 setup.py install
```

Use the `--user` option if you want to install it only for the current user.

# How to use the HTTP library

```
from ppp_libmodule import HttpRequestHandler

def app(environ, start_response):
    """Function called by the WSGI server."""
    return HttpRequestHandler(environ, start_response, RequestHandler).dispatch()
```

Where `RequestHandler` is a class of your own that implements the following
interface:

* `__init__(self, request)`, where `request` is the content of the
  request object sent by a client (deserialized from JSON)
* `answer(self)`, which returns content of the response object to the client
  (must be JSON-serializable.

See the [specification](https://github.com/ProjetPP/Documentation/blob/master/module-communication.md)
to learn more about what those objects are.

`answer` may also raise one of those exceptions:

* `ppp_libmodule.exceptions.ClientError`, which will tell the client their request
  has a problem. The first argument to the exception must contain an explicit
  message
* `ppp_libmodule.exception.InvalidConfig`, raised when the administrator of your
  router did not configure it well.
  Displays the error message in the console and exits

Any other exception is caught and logged, and an “Internal Server Error” is
served to the client.
