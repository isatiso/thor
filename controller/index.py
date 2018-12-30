# coding:utf-8
"""Views Module."""

import time
from tornado import gen
from tornado.options import define
from config import CFG as O_O

from lib.web import BaseController, route


@route(r'/')
class Index(BaseController):
    """Test index request handler."""

    async def get(self, *_args, **_kwargs):
        """Get method of IndexHandler."""
        self.render('index.html')


@route(r'/test(?P<path>.*)?')
class Test(BaseController):
    """Test method."""

    async def get(self, *_args, **_kwargs):
        """Test GET."""
        res = dict(method='GET', path=_kwargs.get('path'), time=time.time())
        # print(self.request.body[:200])
        print('cookie', self.get_current_user(), self.get_parameters())
        self.set_current_user('kjhkjhkjhkjh')
        self.set_parameters(dict(a=1, b=2, c=4))

        self.finish_with_json(res)

    def post(self, *_args, **_kwargs):
        """Test POST."""
        res = dict(method='POST', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)

    def put(self, *_args, **_kwargs):
        """Test PUT."""
        res = dict(method='PUT', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)

    def delete(self, *_args, **_kwargs):
        """Test DELETE."""
        res = dict(method='DELETE', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)