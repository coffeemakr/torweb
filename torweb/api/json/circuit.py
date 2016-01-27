# -*- coding: utf-8 -*-
'''
JSON circuit wrappers
'''
from __future__ import absolute_import

from .base import JsonObjectWrapper

__all__ = ('JsonCircuitMinimal', 'JsonCircuit')


class JsonCircuit(JsonObjectWrapper):
    '''
    Serializable wrapper for Circuit
    '''

    attributes = (
        'id',
        'state',
        'purpose',
        'path',
        'build_flags',
        'time_created',
        'streams'
    )


class JsonCircuitMinimal(JsonCircuit):
    '''
    Minimal wrapper for a circuit.
    '''
    attributes = (
        'id',
        'state',
        'purpose',
        'path',
    )
