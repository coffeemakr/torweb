# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

import zope.interface

from torweb.api.json.router import JsonRouter

from .base import ITorResource, TorResource

__all__ = ('RouterRoot',)


class RouterRoot(TorResource):
    '''
    Router list resource.
    '''
    zope.interface.implements(ITorResource)

    json_detail_class = JsonRouter
    json_list_class = JsonRouter

    def get_list(self):
        '''
        Returns a list of router
        '''
        return self._config.state.routers_by_hash.values()

    def get_by_id(self, ident):
        '''
        Returns a single router by its unique name
        '''
        if not ident.startswith('$'):
            ident = '$' + ident
        if ident not in self._config.state.routers_by_hash:
            return None
        return self._config.state.routers_by_hash[ident]
