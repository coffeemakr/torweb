import json as j
import datetime
def object_to_dict(obj, attributes):
	result = {}
	for attr in attributes:
		value = getattr(obj, attr)
		if isinstance(value, datetime.datetime):
			value = value.isoformat()
		result[attr] = value
	return result

def json(func):
	def new_func(*args):
		request = args[-1]
		request.responseHeaders.addRawHeader("content-type", "application/json")
		return j.dumps(func(*args))
	return new_func