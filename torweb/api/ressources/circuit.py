# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import, print_function, with_statement

from twisted.web import server
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
        '''
        Closes the circuit
        '''
        def close_successfull(arg, request):
            "Close callback"
            print("Close curcuit sucess: ", arg)
            response.send_json(request, {})

        def close_failed(error, request):
            "Close errback"
            print("Close curcuit failed: ", error)
            response.send_json(request, response.error_tb(error))

        deferred = self.object.close()
        deferred.addCallback(close_successfull, request)
        deferred.addErrback(close_failed, request)
        return server.NOT_DONE_YET


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
        if ident not in self._config.state.circuits:
            return None
        return self._config.state.find_circuit(ident)

    def get_list(self):
        return self._config.state.circuits.values()
