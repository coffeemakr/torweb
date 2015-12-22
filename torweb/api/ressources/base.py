# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

from twisted.web import resource

__all__ = ('TorResource',)


class TorResource(resource.Resource):

    def get_torstate(self):
        return self._torstate

    def set_torstate(self, torstate):
        self._torstate = torstate

    torstate = property(get_torstate)

    def __init__(self, torstate=None):
        resource.Resource.__init__(self)
        self._torstate = torstate
