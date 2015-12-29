import json as j


def json(func):
    def new_func(self, request, *args):
        request.json_content = j.loads(
            request.content.getvalue().decode('utf-8'))
        return func(self, request, *args)
    return new_func
