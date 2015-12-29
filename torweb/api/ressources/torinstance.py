# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement


from twisted.web import resource
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor
from autobahn.twisted.resource import WebSocketResource
import txtorcon

from torweb.api.json import JsonTorInstanceMinimal, JsonTorInstance
from torweb.api.util import response
from torweb.api.ressources import CircuitRoot, RouterRoot
from torweb.api.ressources import StreamRoot, ConfigurationRoot
from torweb.api import websocket
from torweb.error import ConfigurationError

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

    def __init__(self, port, host='127.0.0.1', password=None):
        resource.Resource.__init__(self)

        self._password = None
        self._id = None
        self._configuration = None

        self.host = host
        self.port = port

        if password is not None:
            self.set_password(password)

        self.endpoint = TCP4ClientEndpoint(reactor, self.host, port)

        d = self.endpoint.connect(txtorcon.TorProtocolFactory(
            password_function=self._password_callback))
        d.addCallback(self._build_state)
        d.addErrback(self._connection_failed)

        self.circuitRoot = CircuitRoot()
        self.routerRoot = RouterRoot()
        self.streamRoot = StreamRoot()
        self.configRoot = ConfigurationRoot()
        self.putChild('circuit', self.circuitRoot)
        self.putChild('router', self.routerRoot)
        self.putChild('stream', self.streamRoot)
        self.putChild('config', self.configRoot)

        self.websocket_factory = websocket.TorWebSocketServerFactory()
        self.websocket = WebSocketResource(self.websocket_factory)
        self.putChild('websocket', self.websocket)

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
        print('returned password')
        return self._password

    def set_password(self, password):
        self._password = password

    def get_password(self):
        return self._password

    password = property(get_password, set_password)

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

        arguments = ('port', 'host', 'password')
        kwargs = {}
        for keyword in arguments:
            if keyword in config:
                kwargs[keyword] = config[keyword]

        try:
            kwargs['port'] = int(kwargs['port'])
        except ValueError:
            raise ConfigurationError("Port must be an integer.")
        return TorInstance(**kwargs)

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
