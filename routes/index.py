# coding:utf-8

from handlers.index import Index, Test
from tornado.web import StaticFileHandler


INDEX_ROUTES = [
    (r'/', Index),
    (r'/test(?P<path>.*)?', Test),
    (r'/static(?P<path>.*)?', StaticFileHandler),
]
