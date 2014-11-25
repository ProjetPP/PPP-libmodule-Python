"""Configuration module."""

import os
import json
import logging
from collections import namedtuple
from .exceptions import InvalidConfig


class Config:
    __slots__ = ('debug',)
    def __init__(self, data=None):
        if not hasattr(self, 'config_path_variable') or \
                not hasattr(self, 'parse_config'):
            raise NotImplementedError('Config class does not implement all '
                                      'required attributes.')
        self.debug = True
        if not data:
            try:
                with open(self.get_config_path()) as fd:
                    data = json.load(fd)
            except ValueError as exc:
                raise InvalidConfig(*exc.args)
        self.parse_config(data)

    @classmethod
    def get_config_path(cls):
        path = os.environ.get(cls.config_path_variable, '')
        if not path:
            raise InvalidConfig('Could not find config file, please set '
                                'environment variable $%s.' %
                                cls.config_path_variable)
        return path

