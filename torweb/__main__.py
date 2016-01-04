# -*- coding: utf-8 -*-
'''
Execution of package
'''

from __future__ import absolute_import, print_function, with_statement

from . import server
import sys

server.main(sys.argv)
