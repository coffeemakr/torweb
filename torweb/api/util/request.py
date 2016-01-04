import json as j


def json(func):
    def new_func(self, request, *args):
        # TODO: Error handling
        request.json_content = j.loads(
            request.content.getvalue().decode('utf-8'))
        return func(self, request, *args)
    new_func.__doc__ = func.__doc__
    return new_func
