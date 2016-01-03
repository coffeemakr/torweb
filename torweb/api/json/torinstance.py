# -*- coding: utf-8 -*-
'''
JSON tor instance wrapper
'''
from __future__ import absolute_import, print_function, with_statement

from .base import JsonObjectWrapper

__all__ = ('JsonTorInstance', 'JsonTorInstanceMinimal')


class JsonTorInstance(JsonObjectWrapper):
    '''
    JSON wrapper for a single tor instance.
    '''
    attributes = ('id', 'connected', 'host',
                  'port', 'connection_error', 'configuration', 'dns_port')

    @staticmethod
    def _set_json_error(dictionary):
        '''
        Reads the connection errors.
        '''
        if dictionary['connection_error'] is not None:
            error = dictionary['connection_error']
            dictionary['connection_error'] = {
                'message': error.getErrorMessage(),
                'exception': error.type.__name__
            }

    def as_dict(self):
        result = super(JsonTorInstance, self).as_dict()
        self._set_json_error(result)
        return result


class JsonTorInstanceMinimal(JsonTorInstance):
    '''
    Minimal JSON wrapper for a tor instance.
    '''
    attributes = ('id', 'connected', 'host', 'port', 'connection_error')
