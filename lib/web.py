# coding:utf-8
"""Base module for other views' modules."""
import json
import re
import time
import traceback
import os
from functools import wraps
from urllib import parse
import inspect

import jwt
from tornado import gen, httpclient
from tornado.web import Finish, MissingArgumentError, RequestHandler, HTTPError
from tornado.log import app_log, gen_log

from config import get_status_message, CFG as O_O
from lib.entity import Arguments, ParseJSONError
from lib.utils import dump_in, dump_out, dump_error

ROUTES = []


class TokenExpiredError(HTTPError):
    """Token Expired Error."""

    def __init__(self):
        super(TokenExpiredError, self).__init__(400, 'Token Expired.')


def route(path: str):
    def wrapper(handler: RequestHandler):
        if not issubclass(handler, RequestHandler):
            raise PermissionError('Can\'t routing a nonhandler class.')

        filename = traceback.extract_stack(limit=2)[0].filename
        filename = os.path.basename(filename)
        filename = os.path.splitext(filename)[0]
        filename = '' if filename == 'index' else filename

        realpath = path.strip('/')
        realpath = '/' + f'{filename}/{realpath}'.strip('/')
        ROUTES.append((realpath, handler))
        return handler

    return wrapper


def check_auth(func):
    """Check user status."""

    def process(ctlr):
        token_params = Arguments(ctlr.get_token())
        now = int(time.time())
        if not token_params:
            raise MissingArgumentError('unvalid token.')
        if 'timestamp' not in token_params:
            raise MissingArgumentError('no timestamp info in token.')
        if token_params.timestamp < now:
            raise TokenExpiredError()

        params = dict()
        params['token'] = token_params
        params['device'] = ctlr.get_argument('device', 'web')
        params['lang'] = ctlr.get_argument('lang', 'cn').lower()
        params['remote_ip'] = ctlr.request.remote_ip
        params['request_time'] = now

        ctlr.params = Arguments(params)

    @wraps(func)
    async def async_wrapper(ctlr, **kwargs):
        process(ctlr)
        await func(ctlr, **kwargs)

    @wraps(func)
    def wrapper(ctlr, **kwargs):
        process(ctlr)
        func(ctlr, **kwargs)

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return wrapper


class BaseController(RequestHandler):
    """Custom handler for other views module."""

    def __init__(self, application, request, **kwargs):
        super(BaseController, self).__init__(application, request, **kwargs)
        self.params = None

    def _request_summary(self):
        s = ' '
        return f'{self.request.method.rjust(6, s)} {self.request.remote_ip.rjust(15, s)}  {self.request.path} '

    def log_exception(self, typ, value, tb):
        """Override to customize logging of uncaught exceptions.

        By default logs instances of `HTTPError` as warnings without
        stack traces (on the ``tornado.general`` logger), and all
        other exceptions as errors with stack traces (on the
        ``tornado.application`` logger).

        .. versionadded:: 3.1
        """
        if isinstance(value, HTTPError):
            if value.log_message:
                # format = "%d %s: " + value.log_message
                # args = ([value.status_code,
                #          self._request_summary()] + list(value.args))
                gen_log.warning('\033[0;31m' + value.log_message + '\033[0m')
        else:
            app_log.error(
                "Uncaught exception %s\n%r",
                self._request_summary(),
                self.request,
                exc_info=(typ, value, tb))

    async def options(self, *_args, **_kwargs):
        self.set_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
        self.set_header('Access-Control-Allow-Headers', 'Authorization')
        self.success()

    def prepare(self):
        self.set_header('Access-Control-Allow-Origin', '*')

    def get_token(self):
        header_name = O_O.server.token_header or 'Thor-Token'
        token = self.request.headers.get(header_name)
        try:
            return jwt.decode(token, O_O.server.token_secret)
        except jwt.DecodeError:
            return None

    def set_token(self, token_params: dict = None):
        token = jwt.encode(token_params, O_O.server.token_secret)
        self.set_header(O_O.server.token_header or 'Thor-Token', token)

    def parse_form_arguments(self):
        """Parse FORM argument like `get_argument`."""
        if O_O.debug:
            dump_in(f'Input: {self.request.method} {self.request.path}',
                    self.request.body.decode()[:500])

        args = {
            k: v[0].decode()
            for k, v in self.request.arguments.items() if v[0]
        }

        return Arguments(args)

    def parse_json_arguments(self):
        """Parse JSON argument like `get_argument`."""
        if O_O.debug:
            dump_in(f'Input: {self.request.method} {self.request.path}',
                    self.request.body.decode()[:500])

        try:
            req = json.loads(self.request.body.decode('utf-8'))
        except json.JSONDecodeError as exception:
            dump_error(self.request.body.decode())
            raise ParseJSONError(exception.doc)

        if not isinstance(req, dict):
            dump_error(self.request.body.decode())
            raise ParseJSONError('Request body should be a dictonary.')

        return Arguments(req)

    def finish_with_json(self, data):
        """Turn data to JSON format before finish."""
        self.set_header('Content-Type', 'application/json')

        if O_O.debug:
            if self.request.method == 'POST':
                info_list = [
                    f'\033[0mOutput: {self.request.method} {self.request.path}'
                ]
                if self.request.query:
                    query_list = [
                        f'\033[0;32m{i[0]:15s} {i[1]}'
                        for i in parse.parse_qsl(self.request.query)
                    ]
                    info_list.append('\n' + '\n'.join(query_list))
                if self.request.body:
                    info_list.append('\n\033[0;32m' +
                                     self.request.body.decode())
                if data:
                    info_list.append('\n\033[0;33m' + json.dumps(data))
                dump_out(*info_list)

        raise Finish(json.dumps(data).encode())

    def fail(self, status, data=None, polyfill=None, **_kwargs):
        """assemble and return error data."""
        msg = get_status_message(status)
        self.finish_with_json(
            dict(status=status, msg=msg, data=data, **_kwargs))

    def success(self, data=None, msg='Successfully.', **_kwargs):
        """assemble and return error data."""
        self.finish_with_json(dict(status=0, msg=msg, data=data))

    async def wait(self, func, worker_mode=True, args=None, kwargs=None):
        """Method to waiting celery result."""
        if worker_mode:
            async_task = func.apply_async(args=args, kwargs=kwargs)

            while True:
                if async_task.status in ['PENDING', 'PROGRESS']:
                    await gen.sleep(O_O.celery.sleep_time)
                elif async_task.status in ['SUCCESS', 'FAILURE']:
                    break
                else:
                    print('\n\nUnknown status:\n', async_task.status, '\n\n\n')
                    break

            if async_task.status != 'SUCCESS':
                dump_error(f'Task Failed: {func.name}[{async_task.task_id}]',
                           f'    {str(async_task.result)}')
                result = dict(status=1, data=async_task.result)
            else:
                result = async_task.result

            if result.get('status'):
                self.fail(-1, result)
            else:
                return result
        else:
            return func(*args, **kwargs)

    async def fetch(self,
                    api,
                    method='GET',
                    body=None,
                    headers=None,
                    **_kwargs):
        """Fetch Info from backend."""
        body = body or dict()

        _headers = dict(host=self.request.host)
        if headers:
            _headers.update(headers)

        if '://' not in api:
            api = f'http://{O_O.server.back_ip}{api}'

        back_info = await httpclient.AsyncHTTPClient().fetch(
            api,
            method=method,
            headers=_headers,
            body=json.dumps(body),
            raise_error=False,
            allow_nonstandard_methods=True)

        res_body = back_info.body and back_info.body.decode() or None

        if back_info.code >= 400:
            return Arguments(
                dict(http_code=back_info.code, res_body=res_body, api=api))

        try:
            return Arguments(json.loads(res_body))
        except json.JSONDecodeError:
            pass
