import json
import time
import functools

from models import Mongo
from tornado import gen, httpclient
from .base_handler import BaseHandler
from config import get_status_message, CFG as O_O

from lib.arguments import Arguments
from lib.logger import dump_in, dump_out, dump_error
from lib.utils import extract_anywhere_keys


class BaseSessionHandler(BaseHandler, Mongo):

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
            expires=time.time() + O_O.server.expire_time
        )

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
            expires=time.time() + O_O.server.expire_time
        )

    @gen.coroutine
    def get_session_code(self):
        if O_O.database.mongo:
            sess_info = self.session.find_one({
                O_O.database.mongo.session_key:
                self.request.remote_ip
            })
            return sess_info and sess_info.get('session_code')

        return ''

    @gen.coroutine
    def set_session_code(self, code):
        pass


def session_auth(**auth_lambdas):
    def authenticated(method):
        """Check user status."""
        @functools.wraps(method)
        def wrapper(self, * args, **kwargs):
            user_id = self.get_current_user()
            params = self.get_parameters()

            def clean_and_fail(code):
                print(f'clean_and_fail {code}')
                self.clear_all_cookies()
                self.fail(code)

            if not user_id or not params:
                return clean_and_fail(3005)

            if user_id != params.user_id:
                return clean_and_fail(3006)

            # ac_code = self.get_session_code()
            # if ac_code is not '' and params.ac_code != ac_code:
            #     return clean_and_fail(3007)
            # for key in kwargs:
            #     if params[key] != kwargs[key]:
            #         dump_error(f'Auth Key Error: {key}')
            #         return self.fail(4003)

            for auth_lambda in auth_lambdas:
                auth_flag = auth_lambdas.get(auth_lambda)(params)
                if not auth_flag:
                    return self.fail(auth_lambda.split('_')[-1])

            self.set_current_user(self.get_current_user())
            self.set_parameters(self.get_parameters())

            return method(self, *args, **kwargs)
        return wrapper
    return authenticated
