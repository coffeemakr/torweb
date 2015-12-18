# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from torweb.api.json import JsonTorInstanceMinimal, JsonTorInstance
from torweb.api.util import response

from twisted.web import resource
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor
from torweb.api.ressources import CircuitRoot, RouterRoot, StreamRoot
from torweb.api import websocket
from autobahn.twisted.resource import WebSocketResource
import txtorcon
from txtorcon import TorProtocolFactory

__all__ = ('TorInstances', 'TorInstance')

class TorInstance(resource.Resource):
    '''
    A resource for a single tor instance.
    '''
    
    #: State tracker
    sate = None

    port = None
    host = None

    def __init__(self, endpoint):
        resource.Resource.__init__(self)

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
        self.websocket = WebSocketResource(self.websocket_factory)
        self.putChild('websocket', self.websocket)
        self._configuration = None

    def getChild(self, child,  request):
        if not child:
            return self

    def _connection_failed(self, *args):
        print("Connection failed: %s" % args)
        # pass to the next errorback
        return args

    def _connection_bootstrapped(self, *args):
        print("Connection suceeded %s " % args)
        d = txtorcon.TorConfig.from_connection(self.protocol)
        d.addCallback(self._configuration_callback)
        return args

    def _configuration_callback(self, config):
        self._configuration = config

    def _build_state(self, proto):
        self.protocol = proto
        proto.post_bootstrap.addErrback(self._connection_failed)
        proto.post_bootstrap.addCallback(self._connection_bootstrapped)
        self.state = txtorcon.TorState(proto)
        self.circuitRoot.set_torstate(self.state)
        self.routerRoot.set_torstate(self.state)
        self.streamRoot.set_torstate(self.state)
        self.websocket_factory.set_torstate(self.state)
        return proto

    @response.json
    def render_GET(self, request):
        return JsonTorInstance(self).as_dict()

    def password_callback(self):
        print('returned password')
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
    
    @property
    def configuration(self):
        config = []
        if self._configuration is not None:
            for name, value in self._configuration.config_args():
                config.append({"name": name, "value": value})
        return config
                

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
        if not torInstance:
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

    def render_GET(self, request):
        return this.list;



class TorInstanceList(resource.Resource):

    isLeaf = True

    def __init__(self, instances):
        self.instances = instances
    
    @response.json
    def render_GET(self, request):
        result = []
        for instance in self.instances.values():
            result.append(JsonTorInstanceMinimal(instance).as_dict())
        return result