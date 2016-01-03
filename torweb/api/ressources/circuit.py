# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource
import zope.interface

from torweb.api.util import response
from torweb.api.json.circuit import JsonCircuit
from .base import TorResource, TorResourceDetail, ITorResource

__all__ = ('CircuitRoot', 'Circuit')


class Circuit(TorResourceDetail):
    '''
    Resource to render details of a tor circuit.
      * `GET`: Get details (see :meth:`TorResourceDetail.render_GET`)
      * `DELETE`:  Close the circuit (see :meth:`render_DELETE`)
    '''
    @response.json
    def render_DELETE(self, request):
        self.object.close()
        return {}


class CircuitRoot(TorResource):
    '''
    Resource to render lists of tor circuits.
      * `GET`: List of circuits
    '''

    zope.interface.implements(ITorResource)

    json_list_class = JsonCircuit
    json_detail_class = JsonCircuit

    detail_class = Circuit

    def get_by_id(self, ident):
        ident = int(ident)
        if ident not in self.torstate.circuits:
            return None
        return self.torstate.find_circuit(ident)

    def get_list(self):
        return self.torstate.circuits.values()
