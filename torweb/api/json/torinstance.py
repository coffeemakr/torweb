# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement


from .base import JsonObject

__all__ = ('JsonTorInstance', 'JsonTorInstanceMinimal')


class JsonTorInstance(JsonObject):
    attributes = ('id', 'connected', 'host',
                  'port', 'connection_error', 'configuration', 'dns_port')

    def _set_json_error(self, d):
        if d['connection_error'] is not None:
            error = d['connection_error']
            d['connection_error'] = {
                'message': error.getErrorMessage(),
                'exception': error.type.__name__
            }

    def as_dict(self):
        d = super(JsonTorInstance, self).as_dict()
        self._set_json_error(d)
        return d


class JsonTorInstanceMinimal(JsonTorInstance):
    attributes = ('id', 'connected', 'host', 'port', 'connection_error')
