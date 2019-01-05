#!/usr/local/bin/python3
# coding:utf-8
"""Main Module."""
import sys

from tornado import httpserver, ioloop, web, gen
from tornado.options import options

from config import CFG as O_O
from lib.web import ROUTES

import controllers


def main():
    """Entrance Function"""
    controllers.load_controllers()

    for r in ROUTES:
        print(f'{r[0]:30s} {r[1]}')

    tornado_app = web.Application(handlers=ROUTES, **O_O.application)
    tornado_server = httpserver.HTTPServer(tornado_app, **O_O.httpserver)

    tornado_server.listen(O_O.server.port)
    print('\nstart listen...')
    O_O.show()

    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
