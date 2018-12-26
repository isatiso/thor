# coding:utf-8
"""Routes Module."""
from tornado import web
from config import CFG as O_O

ROUTES = []


def route(path):
    def wrapper(handler):
        if not issubclass(handler, web.RequestHandler):
            raise PermissionError('Cant routing a nonhandler class.')
        if path is not None:
            ROUTES.append((path, handler))
        return handler

    return wrapper