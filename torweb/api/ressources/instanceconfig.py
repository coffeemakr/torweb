# -*- coding: utf-8 -*-
from twisted.internet import defer


class TorInstanceConfig(object):
    '''
    Instance configuration
    '''

    #: :class:`txtorcon.TorState` instance
    state = None
    #: The instance ressource
    instance = None
    #: :class:`txtorcon.TorConfig` instance
    configuration = None

    protocol = None

    def __init__(self):
        self.state_built = defer.Deferred()
