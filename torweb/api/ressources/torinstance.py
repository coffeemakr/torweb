# -*- coding: utf-8 -*-
'''
Tor instance classes.
'''
from __future__ import absolute_import, print_function, with_statement


from twisted.web import resource
from twisted.internet import reactor, endpoints
from twisted.names import client

from autobahn.twisted.resource import WebSocketResource
import txtorcon

from .instanceconfig import TorInstanceConfig

from torweb.api import websocket
from torweb.error import ConfigurationError
from torweb.api.json.torinstance import JsonTorInstanceMinimal, JsonTorInstance
from torweb.api.util import response, request

from .circuit import CircuitRoot
from .router import RouterRoot
from .configuration import ConfigurationRoot
from .stream import StreamRoot
from .lookup import DNSRoot

__all__ = ('TorInstances', 'TorInstance')


class TorInstance(resource.Resource):
    '''
    A resource for a single tor instance.
    '''

    #: Tor control port
    port = None

    #: Tor control host
    host = None

    #: Error set if the connection failed.
    connection_error = None

    #: Set to true if the instance is connected to the running tor process
    connected = False

    _protocol = None

    circuits = None
    routers = None
    streams = None
    configs = None

    def __init__(self, password=None):
        resource.Resource.__init__(self)
        self._config = TorInstanceConfig()
        self._password = None
        self._id = None
        self._config.configuration = None
        self._logs = []

        self.host = None
        self.port = None

        if password is not None:
            self.password = password

        self.circuits = CircuitRoot(config=self._config)
        self.routers = RouterRoot(config=self._config)
        self.streams = StreamRoot(config=self._config)
        self.configs = ConfigurationRoot(config=self._config)
        self.dns = DNSRoot()

        self.putChild('circuit', self.circuits)
        self.putChild('router', self.routers)
        self.putChild('stream', self.streams)
        self.putChild('config', self.configs)
        self.websocket_factory = websocket.TorWebSocketServerFactory()
        self.websocket_factory.config = self._config
        self.websocket = WebSocketResource(self.websocket_factory)
        self.putChild('websocket', self.websocket)

    def getChild(self, path, request):
        '''
        If the path is 'dns' is returns either dns api resource or an json
        error if the api is not available because there is no DNSPort.

        Otherwise :class:`resource.NoResource` object is returned.
        '''
        if path == 'dns':
            port = self.dns_port
            if port is None:
                msg = "Tor instance has not DNSPort."
                return response.JsonError(message=msg, name="No DNS")
            else:
                self.dns.config.resolver = client.Resolver(
                    servers=[(self.host, port)])
                return self.dns
        return resource.NoResource()

    def _log(self, message, type_=None):
        '''
        Log a message.
        '''
        self._logs.append()

    def _log_error(self, message):
        '''
        Log an error.
        '''
        self._log(message)

    def connect(self, port, host='127.0.0.1'):
        '''
        Connect to a running tor process.

        :param port: The control port.
        :param host: The host on which the tor process runs.
        '''
        self.host = host
        self.port = port
        self.connected = False
        endpoint = endpoints.TCP4ClientEndpoint(reactor, self.host, self.port)
        protocol_factory = txtorcon.TorProtocolFactory(
            password_function=self._password_callback)
        defered = endpoint.connect(protocol_factory)
        defered.addCallback(self._build_state)
        defered.addErrback(self._connection_failed)

    def _build_state(self, protocol):
        '''
        Callback on successfully established connection.
        This method builds the :attr:`state` from the provided
        protocol.
        '''
        self._protocol = protocol
        protocol.post_bootstrap.addErrback(self._connection_failed)
        protocol.post_bootstrap.addCallback(self._connection_bootstrapped)
        protocol.post_bootstrap.addErrback(self._fatal_error)
        self._config.state = txtorcon.TorState(protocol)
        self._config.state_built.callback(self._config.state)
        return protocol

    def _fatal_error(self, error):
        '''
        Catch unexpected errors
        '''
        print("Fatal error: ", error)
        self.connection_error = error

    @property
    def state(self):
        '''
        Returns a :class:`txtorcon.TorState` or :const:`None`
        '''
        return self._config.state

    def _connection_failed(self, error):
        '''
        Callback for when a connection failed.
        '''
        self.connection_error = error
        print("Connection failed: %s" % error.getBriefTraceback())

    def _connection_bootstrapped(self, *args):
        '''
        Callbox for :attr:`txtorcon.TorControlProtocol.post_bootstrap`.
        '''
        self.connected = True
        self.connection_error = None
        print("Connection succeeded: %s " % args)
        defered = txtorcon.TorConfig.from_connection(self._protocol)
        defered.addCallback(self._configuration_callback)
        defered.addErrback(self._fatal_error)
        return args

    def _bootstrap_failed(self, error):
        '''
        Errorback for when bootstrapping fails.
        '''
        self.connection_error = error
        print("Bootstrapping failed: %s" % error.getBriefTraceback())

    def create(self, config):
        '''
        Create a new tor process.
        :param config: a :class:`txtorcon.TorConfig` object.
        '''
        self.connected = False
        if getattr(config, "ControlPort", 0) == 0:
            raise ValueError("ControlPort has to be set to a non-zero value.")

        self.port = config.ControlPort
        self.host = "127.0.0.1"

        defered = txtorcon.launch_tor(config=config, reactor=reactor)
        defered.addCallback(self._process_success)
        defered.addErrback(self._process_failed)
        defered.addErrback(self._fatal_error)

    def _process_success(self, process):
        '''
        Called when :meth:`create` succeeds.
        '''
        print("Process sucess")
        self._build_state(process.tor_protocol)

    def _process_failed(self, error):
        '''
        Called when :meth:`create` fails.
        '''
        self.connection_error = error
        print("Spawning failed: %s" % error.getBriefTraceback())

    def _configuration_callback(self, config):
        self._config.configuration = config
        self.configs.configuration = config

    def _password_callback(self):
        return self._password

    def __get_password(self):
        '''
        The password to authenticate on the tor control port.
        '''
        return self._password

    def __set_password(self, password):
        '''
        Set the password.
        '''
        self._password = password

    password = property(__get_password, __set_password,
                        doc="Password")

    @property
    def dns_port(self):
        '''
        Returns the dns port on which the tor process listens on.
        '''
        if self._config.configuration is None:
            return None
        if 'DNSPort' not in self._config.configuration.config:
            return None
        ports = self._config.configuration.config['DNSPort']
        try:
            port = ports[0]
        except (TypeError, IndexError):
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
        '''
        Returns :const:`True` is the state is built and :const:`False` if not.
        '''
        return self.state is not None

    @property
    def configuration(self):
        '''
        Returns iterable.
        '''
        if self._config.configuration is not None:
            configs = []
            for name, value in self._config.configuration.config_args():
                configs.append({"name": name, "value": value})
            return configs
        return None

    def __set_id(self, ident):
        '''
        Sets the identifiert of this instance.
        '''
        self._id = ident

    def __get_id(self):
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

    id = property(__get_id, __set_id)

    @response.json
    def render_GET(self, request):
        '''
        Renders this instance as JSON.
        '''
        return JsonTorInstance(self).as_dict()


class TorInstances(resource.Resource):
    '''
    Resource to render lists of tor instances.
    '''

    #: Dictionary containing the tor instances by their IDs.
    instances = None

    def __init__(self, config):
        resource.Resource.__init__(self)
        self.config = config
        self.instances = {}
        for index, config in enumerate(self.config["connections"]):
            instance = self._get_instance_from_config(config)
            instance.id = str(index)
            self.instances[instance.id] = instance

    @staticmethod
    def _get_instance_from_config(config):
        '''
        Returns a :class:`TorInstance` from a configuration entry.
        '''
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

    def getChild(self, torInstance, *args):
        '''
        Returns the torinstance.
        '''
        if torInstance in self.instances:
            return self.instances[torInstance]
        return resource.NoResource("Instances does not exist.")

    @response.json
    def render_GET(self, *args):
        '''
        Returns an instance as JSON
        '''
        result = []
        for instance in self.instances.values():
            result.append(JsonTorInstanceMinimal(instance).as_dict())
        return {'objects': result}

    @response.json
    @request.json
    def render_PUT(self, *args):
        '''
        Create a new instance
        '''
        instance = TorInstance()
        self.instances[instance.id] = instance
        config = txtorcon.TorConfig()
        config.ORPort = 0
        config.SocksPort = 9999
        config.ControlPort = 9090
        instance.create(config)
        return {}
