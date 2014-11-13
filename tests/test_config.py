"""Tests what happens if the config file is invalid."""

import os
import tempfile
from webtest import TestApp
from unittest import TestCase
from ppp_libmodule.exceptions import InvalidConfig
from ppp_libmodule.config import Config as BaseConfig

class PartialConfig(BaseConfig):
    __slots__ = ('foo',)
    config_path_variable = 'PPP_LIBMODULE_TEST'

class Config(BaseConfig):
    __slots__ = ('foo',)
    config_path_variable = 'PPP_LIBMODULE_TEST'
    def parse_config(self, data):
        self.foo = data['foo']

class ConfigTestCase(TestCase):
    def testPartialConfig(self):
        self.assertRaises(NotImplementedError, PartialConfig)
    def testNoConfFile(self):
        self.assertRaises(InvalidConfig, Config)

    def testValidConfig(self):
        config_file = tempfile.NamedTemporaryFile('w+')
        try:
            os.environ['PPP_LIBMODULE_TEST'] = config_file.name
            config_file.write('{"foo": "bar"}')
            config_file.seek(0)
            self.assertEqual(Config().foo, 'bar')
        finally:
            config_file.close()
            del os.environ['PPP_LIBMODULE_TEST']
