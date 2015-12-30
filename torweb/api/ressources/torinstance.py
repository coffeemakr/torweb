# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement


from twisted.web import resource
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor, defer
from autobahn.twisted.resource import WebSocketResource
import txtorcon

from torweb.api.json import JsonTorInstanceMinimal, JsonTorInstance
from torweb.api.util import response, request
from .circuit import CircuitRoot
from .router import RouterRoot
from .configuration import ConfigurationRoot
from .stream import StreamRoot
from .lookup import DNSRoot
from twisted.names import client
from torweb.api import websocket
from torweb.error import ConfigurationError

import tempfile

__all__ = ('TorInstances', 'TorInstance')


class TorInstance(resource.Resource):
    '''
    A resource for a single tor instance.
    '''

    #: State tracker
    state = None

    #: Tor control port
    port = None
    #: Tor control host
    host = None

    #: Error set if the connection failed.
    connection_error = None

    #: Set to true if the instance is connected to the running tor process
    connected = False

    def __init__(self, password=None):
        resource.Resource.__init__(self)

        self._password = None
        self._id = None
        self._configuration = None

        self.host = None
        self.port = None

        if password is not None:
            self.set_password(password)

        self.circuitRoot = CircuitRoot()
        self.routerRoot = RouterRoot()
        self.streamRoot = StreamRoot()
        self.configRoot = ConfigurationRoot()
        self.dnsRoot = DNSRoot(resolver=None)
        
        self.putChild('circuit', self.circuitRoot)
        self.putChild('router', self.routerRoot)
        self.putChild('stream', self.streamRoot)
        self.putChild('config', self.configRoot)
        self.websocket_factory = websocket.TorWebSocketServerFactory()
        self.websocket = WebSocketResource(self.websocket_factory)
        self.putChild('websocket', self.websocket)

    def getChild(self, path, request):
        if path == 'dns':
            port = self.dns_port
            if port is None:
                return response.JsonError(message="Tor instance has not DNSPort.", name="No DNS")
            else:
                self.dnsRoot.config.resolver = client.Resolver(servers=[(self.host, port)])
        return self.dnsRoot

    def connect(self, port, host='127.0.0.1'):
        self.host = host
        self.port = port
        self.endpoint = TCP4ClientEndpoint(reactor, self.host, self.port)
        d = self.endpoint.connect(txtorcon.TorProtocolFactory(
            password_function=self._password_callback))
        d.addCallback(self._build_state)
        d.addErrback(self._connection_failed)

    def _process_success(self, process):
        print("Process sucess")
        self._build_state(process.tor_protocol)

    def _process_failed(self, error):
        self.connected = False
        self.connection_error = error
        print("Spawning failed: %s" % error.getBriefTraceback())

    def _connection_failed(self, error):
        self.connected = False
        self.connection_error = error
        print("Connection failed: %s" % error.getBriefTraceback())

    def _connection_bootstrapped(self, *args):
        self.connected = True
        self.connection_error = None
        print("Connection suceeded %s " % args)
        d = txtorcon.TorConfig.from_connection(self.protocol)
        d.addCallback(self._configuration_callback)
        return args

    def _configuration_callback(self, config):
        self._configuration = config
        self.configRoot.configuration = config

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

    def _password_callback(self):
        return self._password

    def set_password(self, password):
        self._password = password

    def get_password(self):
        return self._password

    password = property(get_password,
                        set_password)

    @property
    def dns_port(self):
        if self._configuration is None:
            return None
        if 'DNSPort' not in self._configuration.config:
            return None
        ports = self._configuration.config['DNSPort']
        try:
            port = ports[0]
        except TypeError, IndexError:
            print("DNSPort has invalid type.")
            return None
        if port != "DEFAULT":
            try:
                return int(port)
            except ValueError as why:
                print("DNSPort is no integer: %s" % why)
        return None

    @property
    def has_state(self):
        return self.state is not None

    @property
    def configuration(self):
        '''
        Returns iterable.
        '''
        if self._configuration is not None:
            configs = []
            for name, value in self._configuration.config_args():
                configs.append({"name": name, "value": value})
            return configs
        return None

    def set_id(self, id):
        '''
        Sets the identifiert of this instance.
        '''
        self._id = id

    def get_id(self):
        '''
        Return the identifier for this instance.
        If the identifier is not set previously, a new identifier is generated
        by calling the :func:`hash` function.
        '''
        if self._id is None:
            ident = hash(self)
            ident *= 10
            if ident < 0:
                ident *= -1
            else:
                ident += 1
            self._id = str(ident)
        return self._id

    id = property(get_id, set_id)

    @response.json
    def render_GET(self, request):
        return JsonTorInstance(self).as_dict()
    
    def create(self, config):
        if getattr(config, "ControlPort", 0) == 0:
            raise ValueError("ControlPort has to be set to a non-zero value.")
        self.port = config.ControlPort
        self.host = "127.0.0.1"
        d = txtorcon.launch_tor(config=config, reactor=reactor)
        d.addCallback(self._process_success)
        d.addErrback(self._process_failed)

class TorInstances(resource.Resource):

    #: Dictionary containing the tor instances by their IDs.
    instances = None

    def __init__(self, config):
        resource.Resource.__init__(self)
        self.config = config
        self.instances = {}
        for i, config in enumerate(self.config["connections"]):
            instance = self._get_instance_from_config(config)
            instance.set_id(str(i))
            self.instances[instance.id] = instance

    def _get_instance_from_config(self, config):
        if 'port' not in config:
            raise ConfigurationError("Port not defined.")
        if 'host' not in config:
            raise ConfigurationError("Host not defined.")
        try:
            port = int(config['port'])
        except ValueError:
            raise ConfigurationError("Port must be an integer.")

        host = config['host']

        password = None
        if 'password' in config:
            password = config['password']

        instance = TorInstance(password=password)
        instance.connect(port=port, host=host)
        return instance

    def getChild(self, torInstance, request):
        '''
        Returns the torinstance.
        '''
        if torInstance in self.instances:
            return self.instances[torInstance]
        return resource.NoResource("Instances does not exist.")

    @response.json
    def render_GET(self, request):
        result = []
        for instance in self.instances.values():
            result.append(JsonTorInstanceMinimal(instance).as_dict())
        return {'objects': result}

    @response.json
    @request.json
    def render_PUT(self, request):
        instance = TorInstance()
        self.instances[instance.id] = instance
        config = txtorcon.TorConfig()
        config.ORPort = 0
        config.SocksPort = 9999
        config.ControlPort = 9090
        instance.create(config)
        return {}