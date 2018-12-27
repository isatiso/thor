# coding:utf-8
"""Routes Module."""
from tornado import web
from config import CFG as O_O
import traceback
from pprint import pprint
import os

ROUTES = []


def route(path):
    def wrapper(handler):
        if not issubclass(handler, web.RequestHandler):
            raise PermissionError('Cant routing a nonhandler class.')
        # print(dir(handler))
        # print(handler.__class__)\
        filename = traceback.extract_stack(limit=2)[0].filename
        filename = os.path.basename(filename)
        filename = os.path.splitext(filename)[0]
        print(filename)
        
        if path is not None:
            ROUTES.append((path, handler))
        return handler

    return wrapper