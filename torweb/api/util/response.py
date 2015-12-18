# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

import json as j

def json(func):
	def new_func(*args):
		request = args[-1]
		request.responseHeaders.addRawHeader("content-type", "application/json")
		result = func(*args)
		if not type(result) == str:
			result = j.dumps(result).encode('utf8')
		return result
	return new_func