import json as j

def json(func):
	def new_func(*args):
		request = args[-1]
		request.responseHeaders.addRawHeader("content-type", "application/json")
		return j.dumps(func(*args))
	return new_func