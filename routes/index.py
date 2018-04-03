# coding:utf-8

from views.index import Index, Test

INDEX_ROUTES = [
    (r'/', Index),
    (r'/test(?P<path>.*)?', Test),
]
