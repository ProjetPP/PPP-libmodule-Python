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

The module creation script should have created a `requesthandler.py` file
with two methods to implement:

* `__init__(self, request)`, where `request` is the content of the
  request object sent by a client (deserialized from JSON)
* `answer(self)`, which returns a list of response objects to the client

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

# How to use the configuration library

`ppp_libmodule` provides a simple wrapper around JSON configuration
files you can use easily.

```
from ppp_libmodule.config import Config as BaseConfig
from ppp_libmodule.exception import InvalidConfig

class Config(BaseConfig):
    config_path_variable = 'PPP_MYMODULE_CONFIG'

    def parse_config(self, data):
        # parse your config here
```

There are two things to implement:

* The name of the configuration variable. This is the name of the
  environment variable that will be read to know where to find
  the configuration file of your module.
  For instance: `PPP_CORE_CONFIG` or `PPP_NLP_CLASSICAL_CONFIG`.
* The configuration parser: it simply takes the deserialized data
  from the file, and sets attributes to the Config object, so your
  module can access it later.
