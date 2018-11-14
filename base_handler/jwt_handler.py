import jwt
import json
import time
import functools
import datetime

from models import Mongo
from tornado import gen, httpclient
from tornado.web import Finish, MissingArgumentError, RequestHandler
from .base_handler import BaseHandler
from config import get_status_message, CFG as O_O
from lib.arguments import Arguments
from lib.logger import dump_in, dump_out, dump_error


jwt_options = {
    'verify_signature': True,
    'verify_exp': True,
    'verify_nbf': False,
    'verify_iat': True,
    'verify_aud': False
}


class BaseJWTHandler(BaseHandler, Mongo):

    def get_current_user(self):
        """Get current user from cookie.
        p.s. self.get_secure_cookie 方法只会返回 None 或者 bytes."""
        user_id = self.get_secure_cookie(O_O.server.cookie_name.user_id)
        return user_id and user_id.decode()

    # def set_current_user(self, user_id=''):
    #     """Set current user to cookie."""
    #     self.set_secure_cookie(
    #         name=O_O.server.cookie_name.user_id,
    #         value=user_id,
    #         expires=time.time() + O_O.server.expire_time,
    #         domain=self.request.host)

    def get_parameters(self):
        """Get user information from cookie."""
        jwt_token = self.request.headers.get('Authorization')
        if jwt_token:
            parts = jwt_token.split()
            if parts[0].lower() != 'bearer':
                self._transforms = []
                self.fail(3401)
            elif len(parts) == 1:
                self._transforms = []
                self.fail(3401)
            elif len(parts) > 2:
                self._transforms = []
                self.fail(3401)
            token = parts[1]
            try:
                # en = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJ3YXBpLmNvbSIsImF1ZCI6Ind3dy53YXBpLmNvbSIsInVzZXJuYW1lIjoiXHU3MzhiXHU0ZTlhXHU5Zjk5Iiwic2NvaXBlcyI6WyJvcGVuIl0sImRhdGEiOnsid3NJZCI6IjE3MDQyNzQ0IiwibmFtZSI6Ilx1NzM4Ylx1NGU5YVx1OWY5OSIsImVtcEdyYWRlIjoiVDMuMiIsIm1haWwiOiJ3YW5neWxAd29uZGVyc2hhcmUuY24iLCJkZXBJZCI6IllGVzIwMiIsImRlcElkMSI6IlBFMDAxIiwiam9iQ05hbWUiOiJcdTlhZDhcdTdlYTdcdTU0MGVcdTdhZWZcdThmNmZcdTRlZjZcdTVmMDBcdTUzZDFcdTVkZTVcdTdhMGJcdTVlMDgiLCJkZXBDTmFtZSI6Ilx1NGU5MVx1NjcwZFx1NTJhMVx1N2VjNCIsInBvc3RDbGFzc2lmaWNhdGlvbiI6Ilx1NjczYVx1NWJjNiIsInJlcG9ydFRvIjoiXHU2NzMxXHU1ZTM4XHU2ZDliIiwiam9pbkRhdGUiOiIyMDE3LTA0LTI1IiwiYXZhdGFyIjoiMTQ5MzI3NDM3NDY1NzAzMi5wbmciLCJoclR5cGUiOm51bGwsIm1vdHRvIjpudWxsLCJjb250YWN0IjpudWxsLCJmb2N1c0FncmVlIjpudWxsLCJhdmdIb3VycyI6Ny40NSwibGVhdmVIb3VycyI6MS4wLCJuZWVkQXR0ZW5kIjo1Mi41LCJhdHRlbmQiOjUyLjEzLCJsYXRlVGltZXMiOjAsImxhdGVyTWludXRlcyI6MC4wLCJhbm51YWxMZWF2ZSI6MC4wLCJ0b3RhbExlYXZlIjo1LCJvYVNpZ25UaW1lcyI6MH0sImlhdCI6MTUzNjczMzI1MC45Njk3ODY2LCJleHAiOjE1MzY3MzMyNzJ9.9fSmLWL-90XDP3zy_2APJWAvf_mJYD91c0CVTeUIm94'
                params = jwt.decode(token,
                                    O_O.security_key,
                                    options=jwt_options,
                                    algorithms=['HS256']
                                    )
            except jwt.InvalidTokenError:
                print('InvalidTokenError')
                self._transforms = []
                self.fail(3401)

            except jwt.exceptions.MissingRequiredClaimError:
                print('MissingRequiredClaimError')
                self.fail(3401)
            except jwt.ExpiredSignatureError:
                print('ExpiredSignatureError')
                self.fail(3402)
            except jwt.InvalidIssuedAtError:
                print('InvalidIssuedAtError')
                self.fail(3403)

            except Exception as e:
                self._transforms = []
                self.fail(3152)
        else:
            self._transforms = []
            # raise MissingArgumentError('header:Authorization ')
            self.fail(4000)
        # print(params.get('data'))
        return Arguments(params and params.get('data'))

    # def set_parameters(self, params=''):
    #     """Set user information to the cookie."""
    #     if not isinstance(params, dict):
    #         raise ValueError('params should be <class \'dict\'>')
    #     self.set_secure_cookie(
    #         name=O_O.server.cookie_name.parameters,
    #         value=json.dumps(params),
    #         expires=time.time() + O_O.server.expire_time,
    #         domain=self.request.host)
    def get_authorization_code(self, params, expire_time=1):
        token = jwt.encode({
            'iss': self.request.host,
            'aud': self.request.host,
            # 'username': f'{login_data.name}',
            'scoipes': ['open'],
            'data': params,
            'iat': int(time.time()),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expire_time)},
            O_O.security_key,
            algorithm='HS256'
        )
        return dict(token=token.decode())

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


def jwt_auth(**auth_lambdas):
    def authenticated(method):
        @functools.wraps(method)
        def wrapper(self, permission=None, *args, **kwargs):
            params = self.get_parameters()

            for auth_lambda in auth_lambdas:
                auth_flag = auth_lambdas.get(auth_lambda)(params)
                if not auth_flag:
                    return self.fail(auth_lambda.split('_')[-1])

            return method(self, *args, **kwargs)
        return wrapper
    return authenticated
