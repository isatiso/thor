# coding:utf-8
"""Base module for other views' modules."""
import json
import re
import time

from tornado import gen, httpclient
from tornado.web import Finish, MissingArgumentError, RequestHandler
from models import Mongo
from config import get_status_message, CFG as O_O
from lib.arguments import Arguments
from lib.errors import ParseJSONError
from lib.logger import dump_in, dump_out, dump_error

ENFORCED = True
OPTIONAL = False


class BaseHandler(RequestHandler, Mongo):
    """Custom handler for other views module."""

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.params = None

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

    def get_parameters(self):
        """Get user information from cookie."""
        params = self.get_secure_cookie(O_O.server.cookie_name.parameters)
        return Arguments(params and json.loads(params.decode()))

    def set_parameters(self, params=''):
        """Set user information to the cookie."""
        if not isinstance(params, dict):
            raise ValueError('params should be <class \'dict\'>')
        self.set_secure_cookie(
            name=O_O.server.cookie_name.parameters,
            value=json.dumps(params),
            expires=time.time() + O_O.server.expire_time,
            domain=self.request.host)

    @gen.coroutine
    def get_session_code(self):
        if O_O.mongo:
            sess_info = self.session.find_one({
                O_O.mongo.session_key:
                self.request.remote_ip
            })
            return sess_info and sess_info.get('session_code')

        return ''

    @gen.coroutine
    def set_session_code(self, code):
        pass

    def fail(self, status, data=None, polyfill=None, **_kwargs):
        """assemble and return error data."""
        msg = get_status_message(status)
        self.finish_with_json(
            dict(status=status, msg=msg, data=data, **_kwargs))

    def success(self, msg='Successfully.', data=None, **_kwargs):
        """assemble and return error data."""
        self.finish_with_json(dict(status=0, msg=msg, data=data))

    @gen.coroutine
    def fetch(self, api, method='GET', body=None, headers=None, **_kwargs):
        """Fetch Info from backend."""
        body = body or dict()

        _headers = dict(host=self.request.host)
        if headers:
            _headers.update(headers)

        if '://' not in api:
            api = f'http://{O_O.server.back_ip}{api}'

        back_info = yield httpclient.AsyncHTTPClient().fetch(
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

    @gen.coroutine
    def check_auth(self, check_level=1):
        """Check user status."""
        user_id = self.get_current_user()
        params = self.get_parameters()

        def fail(code):
            self.set_current_user('')
            self.set_parameters({})
            self.fail(code)

        if not user_id or not params:
            fail(3005)

        if user_id != params.user_id:
            fail(3006)

        ac_code = yield self.get_session_code()
        if ac_code is not '' and params.ac_code != ac_code:
            fail(3007)

        self.set_current_user(self.get_current_user())
        self.set_parameters(self.get_parameters().arguments)
        return params

    def parse_form_arguments(self, **keys):
        """Parse FORM argument like `get_argument`."""
        if O_O.debug:
            dump_in(f'Input: {self.request.method} {self.request.path}',
                    self.request.body.decode()[:500])

        req = dict()
        for key in keys:
            if keys[key] is ENFORCED:
                req[key] = self.get_argument(key)
            elif keys[key] is OPTIONAL:
                req[key] = self.get_argument(key, None)

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

        return Arguments(req)

    def parse_json_arguments(self, **keys):
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

        for key in keys:
            if keys[key] is ENFORCED and key not in req:
                dump_error(self.request.body.decode())
                raise MissingArgumentError(key)

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

        return Arguments(req)

    def finish_with_json(self, data):
        """Turn data to JSON format before finish."""
        self.set_header('Content-Type', 'application/json')
        if O_O.debug:
            dump_out(f'Output: {self.request.method} {self.request.path}',
                     str(data))

        raise Finish(json.dumps(data).encode())

    # def pattern_match(self, pattern_name, string):
    #     """Check given string."""
    #     return re.match(self.pattern[pattern_name], string)
