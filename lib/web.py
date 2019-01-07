# coding:utf-8
"""Base module for other views' modules."""
import json
import re
import time
import traceback
import os

from urllib import parse

from tornado import gen, httpclient
from tornado.web import Finish, MissingArgumentError, RequestHandler, HTTPError
from tornado.log import app_log, gen_log

from config import get_status_message, CFG as O_O
from lib.entity import Arguments, ParseJSONError
from lib.utils import dump_in, dump_out, dump_error

ROUTES = []


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
        print('loaded', realpath)

        return handler

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

    def get_current_user(self):
        """Get current user from cookie.
        p.s. self.get_secure_cookie 方法只会返回 None 或者 bytes."""
        user_id = self.get_secure_cookie(O_O.server.cookie_name.user_id)
        return user_id and user_id.decode()

    def set_current_user(self, user_id=''):
        """Set current user to cookie."""
        self.set_secure_cookie(
            name=O_O.server.cookie_name.user_id,
            value=user_id,
            expires=time.time() + O_O.server.expire_time,
            domain=self.request.host)

    # def get_parameters(self):
    #     """Get user information from cookie."""
    #     params = self.get_secure_cookie(O_O.server.cookie_name.parameters)
    #     return Arguments(params and json.loads(params.decode()))

    # def set_parameters(self, params=''):
    #     """Set user information to the cookie."""
    #     if not isinstance(params, dict):
    #         raise ValueError('params should be <class \'dict\'>')
    #     self.set_secure_cookie(
    #         name=O_O.server.cookie_name.parameters,
    #         value=json.dumps(params),
    #         expires=time.time() + O_O.server.expire_time,
    #         domain=self.request.host)

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

    # @gen.coroutine
    # def check_auth(self, **kwargs):
    #     """Check user status."""

    #     super_access = self.get_argument('super_access', '')
    #     if super_access == '0x00544':
    #         return Arguments(dict(super_access=super_access))

    #     token = self.get_argument('token', '')
    #     device = self.get_argument('device', 'web')
    #     lang = self.get_argument('lang', 'cn').lower()

    #     user_id = token_bar.get_token(token, device=device_num)
    #     if not user_id:
    #         self.fail(1001)
    #     token_bar.set_token(token, user_id, xx=True, device=device_num)

    #     params = yield self.get_user_info(user_id)

    #     if not params:
    #         self.fail(1001)
    #     params['token'] = token
    #     params['device'] = device_num
    #     params['lang'] = lang

    #     for key in kwargs:
    #         if key not in params:
    #             dump_error('Exception:\n', f'Auth Key Error: {key}')
    #             self.fail(403, data=dict())

    #         if not isinstance(kwargs[key], list):
    #             if params[key] != kwargs[key]:
    #                 dump_error('Exception:\n', f'Auth Key Error: {key}')
    #                 self.fail(403, data=dict())
    #         else:
    #             operator = kwargs[key][0]
    #             value = kwargs[key][1]

    #             if not OPERATORS[operator](params[key], value):
    #                 dump_error('Exception:\n', f'Auth Key Error: {key}')
    #                 self.fail(400, data=dict())

    #     result = Arguments(params)
    #     self.params = result
    #     return result

    def parse_form_arguments(self, *enforced_keys, **optional_keys):
        """Parse FORM argument like `get_argument`."""
        if O_O.debug:
            dump_in(f'Input: {self.request.method} {self.request.path}',
                    self.request.body.decode()[:500])

        req = dict()
        for key in enforced_keys:
            req[key] = self.get_argument(key)
        for key in optional_keys:
            values = self.get_arguments(key)
            if len(values) is 0:
                req[key] = optional_keys.get(key)
            elif len(values) is 1:
                req[key] = values[0]
            else:
                req[key] = values

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

        return Arguments(req)

    def parse_json_arguments(self, *enforced_keys, **optional_keys):
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
            raise ParseJSONError('Req should be a dictonary.')

        for key in enforced_keys:
            if key not in req:
                dump_error(self.request.body.decode())
                raise MissingArgumentError(key)

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

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
