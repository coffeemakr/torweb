# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

import json

import txtorcon
from zope.interface import implements
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory

from torweb.api.json.circuit import JsonCircuit
from torweb.api.json.stream import JsonStream


__all__ = ('TorWebSocketServerFactory',)

EVENT_TYPE_CIRCUIT = "circuit"
EVENT_TYPE_STREAM = "stream"
EVENT_CIRCUIT_NEW = "new"
EVENT_CIRCUIT_LAUNCHED = "launched"
EVENT_CIRCUIT_EXTEND = "extend"
EVENT_CIRCUIT_BUILT = "built"
EVENT_CIRCUIT_CLOSED = "closed"
EVENT_CIRCUIT_FAILED = "failed"

EVENT_STREAM_NEW = "new"
EVENT_STREAM_SUCCEEDED = "succeeded"
EVENT_STREAM_ATTACH = "attach"
EVENT_STREAM_DETACH = "detach"
EVENT_STREAM_CLOSED = "closed"
EVENT_STREAM_FAILED = "failed"


class MyServerProtocol(WebSocketServerProtocol):
    implements(txtorcon.ICircuitListener, txtorcon.IStreamListener)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            payload = json.loads(payload.decode('utf8'))
        # ignore messae

    def onConnect(self, request):
        print("Client connecting: {}".format(request.peer))

    def onOpen(self):
        # self.sendMessage("hello")
        print("WebSocket connection open.")

    def send_event(self, event, data):
        '''
        Sends an event to the connected client.
        '''
        payload = {
            'type': event,
            'data': data
        }
        self.sendMessage(json.dumps(payload).encode('utf8'))

    def send_circuit_event(self, action, circuit):
        '''
        Sends a circuit event to the connected client.
        '''
        json_circuit = JsonCircuit(circuit).as_dict()

        event = {'action': action,
                 'circuit': json_circuit}

        self.send_event(EVENT_TYPE_CIRCUIT, event)

    def send_stream_event(self, action, stream):
        '''
        Sends a stream event to the connected client.
        '''
        json_stream = JsonStream(stream).as_dict()

        if 'circuit' in json_stream and json_stream['circuit'] == None:
            # Don't send removed circuit
            del json_stream['circuit']

        event = {'action': action,
                 'stream': json_stream}

        self.send_event(EVENT_TYPE_STREAM, event)

    def circuit_new(self, circuit):
        '''
        Circuit listener method
        '''
        self.send_circuit_event(EVENT_CIRCUIT_NEW, circuit)

    def circuit_launched(self, circuit):
        '''
        Circuit listener method
        '''
        self.send_circuit_event(EVENT_CIRCUIT_LAUNCHED, circuit)

    def circuit_extend(self, circuit, router):
        '''
        Circuit listener method
        '''
        self.send_circuit_event(EVENT_CIRCUIT_EXTEND, circuit)

    def circuit_built(self, circuit):
        '''
        Circuit listener method
        '''
        self.send_circuit_event(EVENT_CIRCUIT_BUILT, circuit)

    def circuit_closed(self, circuit, **kwargs):
        '''
        Circuit listener method
        '''
        self.send_circuit_event(EVENT_CIRCUIT_CLOSED, circuit)

    def circuit_failed(self, circuit, **kw):
        '''
        Circuit listener method
        '''
        self.send_circuit_event(EVENT_CIRCUIT_FAILED, circuit)

    def stream_new(self, stream):
        '''
        Stream listener method
        '''
        self.send_stream_event(EVENT_STREAM_NEW, stream)

    def stream_succeeded(self, stream):
        '''
        Stream listener method
        '''
        self.send_stream_event(EVENT_STREAM_SUCCEEDED, stream)

    def stream_attach(self, stream, circuit):
        '''
        Stream listener method
        '''
        self.send_stream_event(EVENT_STREAM_ATTACH, stream)

    def stream_detach(self, stream, **kw):
        '''
        Stream listener method
        '''
        self.send_stream_event(EVENT_STREAM_DETACH, stream)

    def stream_closed(self, stream, **kw):
        '''
        Stream listener method
        '''
        self.send_stream_event(EVENT_STREAM_CLOSED, stream)

    def stream_failed(self, stream, **kw):
        '''
        Stream listener method
        '''
        self.send_stream_event(EVENT_STREAM_FAILED, stream)


class TorWebSocketServerFactory(WebSocketServerFactory):
    '''
    Websocket Factory which produces :class:`MyServerProtocol`.
    '''

    protocol = MyServerProtocol

    state = None

    def set_torstate(self, state):
        '''
        Set the torstate
        '''
        self.state = state
        return state

    def buildProtocol(self, *args, **kwargs):
        proto = super(TorWebSocketServerFactory,
                      self).buildProtocol(*args, **kwargs)
        if self.state:
            self.state.add_circuit_listener(proto)
            self.state.add_stream_listener(proto)
        else:
            print("no listeners added!")
        return proto
