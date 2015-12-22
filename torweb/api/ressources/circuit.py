# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource
from torweb.api.util import response
from torweb.api.json import JsonCircuit
from .base import TorResource

__all__ = ('CircuitRoot', 'CircuitList', 'Circuit')


class CircuitRoot(TorResource):

    def getChild(self, path, request):
        if not path:
            return CircuitList(self.torstate)
        try:
            return Circuit(self.torstate.circuits[int(path)])
        except KeyError, ValueError:
            return resource.NoResource("No such circuit.")


class CircuitList(TorResource):

    @response.json
    def render_GET(self, request):
        result = []
        for c in self.torstate.circuits.values():
            result.append(JsonCircuit(c).as_dict())
        return result


class Circuit(resource.Resource):

    isLeaf = True

    def __init__(self, circuit):
        resource.Resource.__init__(self)
        self.circuit = circuit

    @response.json
    def render_GET(self, request):
        return JsonCircuit(self.circuit).json()

    @response.json
    def render_DELETE(self, request):
        self.circuit.close()
        return {}
