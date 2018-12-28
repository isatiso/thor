#!/usr/local/bin/python3
# coding:utf-8
"""Main Module."""
import importlib
import sys
import os
from os.path import abspath, join, dirname, splitext

from tornado import httpserver, ioloop, web, gen
from tornado.options import options

from config import CFG as O_O
from lib.web import ROUTES
import controller

import pkgutil
import itertools

def main():
    """Entrance Function"""
    # print(pkgutil)
    print(dir(pkgutil))
    print(controller.__path__)
    # modules_gen = pkgutil.iter_modules('.')
    for i in pkgutil.walk_packages('.thor.controller'):
        print(i)
        print(dir(i))
        print(i.__contains__)

    # print(dir(controller))
 
    # print(controller.__package__)
    # print(controller.__file__)

    # loader = controller.__loader__
    # print(loader)
    # print(dir(loader))

    # os.path.listdir(controller.__path__)

    for r in ROUTES:
        print(f'{r[0]:30s} {r[1]}')

    # tornado_app = web.Application(handlers=ROUTES, **O_O.application)
    # tornado_server = httpserver.HTTPServer(tornado_app, **O_O.httpserver)

    # tornado_server.listen(O_O.server.port)
    # print('\nstart listen...')
    # O_O.show()

    # ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
