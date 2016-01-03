# -*- coding: utf-8 -*-
'''
JSON stream wrapper.
'''
from __future__ import absolute_import, print_function, with_statement

from .base import JsonObjectWrapper
from .circuit import JsonCircuitMinimal

__all__ = ('JsonStream',)


class JsonStream(JsonObjectWrapper):
    '''
    Json wrapper for stream objects.
    '''
    attributes = (
        'id',
        'state',
        'target_host',
        'target_addr',
        'target_port',
        'source_addr',
        'source_port',
        'circuit'
    )

    #: Convert the state to a text.
    state_text = {
        'NEW': 'New request to connect',
        'NEWRESOLVE': 'New request to resolve an address',
        'REMAP': 'Address re-mapped to another',
        'SENTCONNECT': 'Sent a connect cell along a circuit',
        'SENTRESOLVE': 'Sent a resolve cell along a circuit',
        'SUCCEEDED': 'Received a reply; stream established',
        'FAILED': 'Stream failed and not retriable',
        'CLOSED': 'Stream closed',
        'DETACHED': 'Detached from circuit; still retriable',
    }

    def as_dict(self):
        result = super(JsonStream, self).as_dict()
        if result['circuit'] is not None:
            result['circuit'] = JsonCircuitMinimal(result['circuit']).as_dict()
        if result['state'] in self.state_text:
            result['state_text'] = self.state_text[result['state']]
        else:
            result['state_text'] = None
        return result
