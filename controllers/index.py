# coding:utf-8
"""Views Module."""
import inspect
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
        self.set_token(dict(a=1, b=23))
        print(self.get_token())
        print(self.request.headers)
        self.render('index.html')


@route(r'/test(?P<path>.*)?')
class Test(BaseController):
    """Test method."""

    async def get(self, *_args, **_kwargs):
        """Test GET."""
        res = dict(method='GET', path=_kwargs.get('path'), time=time.time())
        self.finish_with_json(res)

    async def post(self, *_args, **_kwargs):
        """Test POST."""
        res = dict(method='POST', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)

    async def put(self, *_args, **_kwargs):
        """Test PUT."""
        res = dict(method='PUT', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)

    async def delete(self, *_args, **_kwargs):
        """Test DELETE."""
        res = dict(method='DELETE', path=_kwargs.get('path'))
        print(self.request.body[:200])
        self.finish_with_json(res)