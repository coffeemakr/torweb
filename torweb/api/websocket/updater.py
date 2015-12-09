from __future__ import print_function
#from twisted.web.websocket import WebSocketHandler
from autobahn.twisted.forwarder import DestEndpointForwardingProtocol
from autobahn.twisted.resource import WebSocketResource
import autobahn.twisted.websocket
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory
import json
import txtorcon
from zope.interface import implements
from torweb.api.json import JsonCircuit, JsonStream
class WebsocketMessage(object):
    def json(self):
        return json.dumps(self.obj, ensure_ascii=False).encode('utf8')

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
        #self.sendMessage("hello")
        print("WebSocket connection open.")


    def sendEvent(self, event, data):
        payload = {
            'type': event,
            'data': data
        }
        self.sendMessage(json.dumps(payload).encode('utf8'))

    def sendCircuitEvent(self, action, circuit):
        self.sendEvent(EVENT_TYPE_CIRCUIT, 
            {
                'action': action,
                'circuit': JsonCircuit(circuit).as_dict()
            });


    def sendStreamEvent(self, action, stream):
        self.sendEvent(EVENT_TYPE_STREAM, 
            {
                'action': action,
                'stream': JsonStream(stream).as_dict()
            });

    def circuit_new(self, circuit):
        self.sendCircuitEvent(EVENT_CIRCUIT_NEW, circuit)

    def circuit_launched(self, circuit):
        self.sendCircuitEvent(EVENT_CIRCUIT_LAUNCHED, circuit)

    def circuit_extend(self, circuit, router):
        self.sendCircuitEvent(EVENT_CIRCUIT_EXTEND, circuit)

    def circuit_built(self, circuit):
        self.sendCircuitEvent(EVENT_CIRCUIT_BUILT, circuit)

    def circuit_closed(self, circuit, **kw):
        self.sendCircuitEvent(EVENT_CIRCUIT_CLOSED, circuit)

    def circuit_failed(self, circuit, **kw):
        self.sendCircuitEvent(EVENT_CIRCUIT_FAILED, circuit)



    def stream_new(self, stream):
        self.sendStreamEvent(EVENT_STREAM_NEW, stream)

    def stream_succeeded(self, stream):
        self.sendStreamEvent(EVENT_STREAM_SUCCEEDED, stream)

    def stream_attach(self, stream, circuit):
        self.sendStreamEvent(EVENT_STREAM_ATTACH, stream)

    def stream_detach(self, stream, **kw):
        self.sendStreamEvent(EVENT_STREAM_DETACH, stream)

    def stream_closed(self, stream, **kw):
        self.sendStreamEvent(EVENT_STREAM_CLOSED, stream)

    def stream_failed(self, stream, **kw):
        self.sendStreamEvent(EVENT_STREAM_FAILED, stream)

def get_server_factory(connection):
    factory = TorWebSocketServerFactory()
    factory.protocol = MyServerProtocol
    tor_connection = txtorcon.build_tor_connection(connection)
    tor_connection.addCallback(factory.setState)
    return factory

class TorWebSocketServerFactory(WebSocketServerFactory):
    def setState(self, state):
        print("state set!!!")
        self.state = state;

    def buildProtocol(self, *args, **kwargs):
        proto = super(TorWebSocketServerFactory, self).buildProtocol(*args, **kwargs)
        self.state.add_circuit_listener(proto)
        self.state.add_stream_listener(proto)
        print("listener added!")
        return proto


def get_ressource(*args, **kwargs):
    return WebSocketResource(get_server_factory(*args, **kwargs))