from __future__ import absolute_import

# NOTE: We use a slightly customized version of the TorControlProtocol
from torweb.api.util.torprotocol import TorProtocolFactory
from torweb.api.json import JsonObject
from torweb.api.util import response

from twisted.web import resource
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor
from torweb.api.ressources import CircuitRoot, RouterRoot, StreamRoot
from torweb.api import websocket
import txtorcon

__all__ = ('TorInstances', 'TorInstance')

class TorInstance(resource.Resource, JsonObject):
    '''
    A resource for a single tor instance.
    '''
    
    #: State tracker
    sate = None

    attributes = ('id', 'is_connected', 'host', 'port')

    port = None
    host = None

    def __init__(self, endpoint):
        resource.Resource.__init__(self)
        JsonObject.__init__(self, self)

        d = endpoint.connect(TorProtocolFactory(password_function=self.password_callback))
        d.addCallback(self._build_state)
        d.addErrback(self._connection_failed)

        self.circuitRoot = CircuitRoot()
        self.routerRoot = RouterRoot()
        self.streamRoot = StreamRoot()

        self.putChild('circuit', self.circuitRoot)
        self.putChild('router', self.routerRoot)
        self.putChild('stream', self.streamRoot)

        self.websocket_factory = websocket.TorWebSocketServerFactory()
        self.websocket = websocket.WebSocketResource(self.websocket_factory)
        self.putChild('websocket', self.websocket)

    def _connection_failed(self, *args):
        print "Connection failed! " + str(args)
        # pass to the next errorback
        return args


    def _build_state(self, proto):
        self.protocol = proto
        proto.post_bootstrap.addErrback(self._connection_failed)

        self.state = txtorcon.TorState(proto)
        self.circuitRoot.set_torstate(self.state)
        self.routerRoot.set_torstate(self.state)
        self.streamRoot.set_torstate(self.state)
        self.websocket_factory.set_torstate(self.state)
        return proto

    @response.json
    def render_GET(self, request):
        print self.as_dict()
        return self.as_dict()

    def password_callback(self):
        print ('returned password')
        return "secret"

    @property
    def has_state(self):
        return self.state is not None
    
    @property
    def is_connected(self):
        return True

    @classmethod
    def from_port(cls, port):
        endpoint = TCP4ClientEndpoint(reactor, "127.0.0.1", port)
        obj = cls(endpoint)
        # TODO: change hacky way to set attributes
        obj.port = port
        obj.host = 'localhost'
        return obj


    @classmethod
    def from_configuration(cls, config):
        if 'port' in config:
            return cls.from_port(config['port'])
        raise ValueError()

    def set_id(self, id):
        self._id = id

    def get_id(self):
        return self._id

    id = property(get_id, set_id)

class TorInstances(resource.Resource):

    #: Dictionary containing the tor instances by their IDs.
    instances = None

    def __init__(self, config):
        resource.Resource.__init__(self)
        self.config = config
        self.instances = {}
        self.list = TorInstanceList(self.instances)
        for i, config in enumerate(self.config["connections"]):
            self.instances[i] = TorInstance.from_configuration(config)
            self.instances[i].set_id(i)
        
        render_GET = self.list.render_GET

    def getChild(self, torInstance, request):
        if torInstance == '':
            return self.list
        child = None
        try:
            torInstance = int(torInstance)
        except ValueError:
            return resource.NoResource("No such instance")
        if torInstance in self.instances:
            child = self.instances[torInstance]
        if child is None:
            child = resource.NoResource("Instances does not exist")
        return child



class TorInstanceList(resource.Resource):

    isLeaf = True

    def __init__(self, instances):
        self.instances = instances
    
    @response.json
    def render_GET(self, request):
        result = []
        for instance in self.instances.values():
            result.append(instance.as_dict())
        return result