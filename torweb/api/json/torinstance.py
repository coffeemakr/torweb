# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement


from .base import JsonObject

__all__ = ('JsonTorInstance', 'JsonTorInstanceMinimal')


class JsonTorInstanceMinimal(JsonObject):
    attributes = ('id', 'is_connected', 'host', 'port')


class JsonTorInstance(JsonObject):
    attributes = ('id', 'is_connected', 'host', 'port', 'configuration')
