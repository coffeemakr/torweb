# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource
from torweb.api.util import response
from torweb.api.json import JsonCircuit
from .base import TorResource, TorResourceDetail

__all__ = ('CircuitRoot', 'Circuit')


class Circuit(TorResourceDetail):

    @response.json
    def render_DELETE(self, request):
        self.object.close()
        return {}


class CircuitRoot(TorResource):

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
