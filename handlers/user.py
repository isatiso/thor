# coding:utf-8
"""Handlers."""
import time
from tornado import web, gen

from base_handler import BaseAuthHandler,  auth
from workers.task_database import DATABASE_TASK as db_task
from lib.others.check import pattern
from lib.utils import figure_id, security_encode, security_decode

from config import CFG as O_O


class User(BaseAuthHandler):
    """Test method."""

    @web.asynchronous
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        """Test GET."""
        args = self.parse_json_arguments(page_number=1, page_size=20, options=[
            'user_id', 'email', 'register_time', 'permission', 'first_name', 'last_name', 'company', 'title', 'country', 'avatar', 'register_ip', 'industry', 'expire_time', 'login_inc'])

        db_users = yield self.wait(db_task.query_user_pagination, kwargs=args)
        if not db_users.get('status'):
            return self.fail(3999, data=db_users)
        data_list, paging = db_users.get('data')
        res = dict(
            result=1,
            status=0,
            data=(data_list, paging),
            msg='Fetch payment record successfully.')
        self.finish_with_json(res)


class UserCheckHandler(BaseAuthHandler):
    """Test method."""

    @web.asynchronous
    @gen.coroutine
    def post(self, *_args, **_kwargs):
        """Test GET."""
        args = self.parse_json_arguments('email', 'password', 'login_time')

        # args.insert('options', ['user_id', 'email', 'register_time', 'permission', 'first_name', 'last_name',
        #                         'company', 'title', 'country', 'avatar', 'register_ip', 'industry', 'expire_time', 'login_inc'])
        # print(args)
        db_users = yield self.wait(db_task.query_account, kwargs=args)
        if db_users.get('status'):
            return self.fail(3999, data=db_users)

        back_data = db_users.get('data')

        if not back_data:
            return self.fail(3011, )

        u_password = security_decode(back_data['password'])

        if not u_password or u_password != args.password:
            return self.fail(3001)

        del back_data['password']

        _ = yield self.wait(db_task.update_account_login_inc, kwargs=dict(user_id=back_data['user_id']), waiting=False)

        params = self.bind_params(back_data)
        if O_O.auth_storage == 'JWT':
            print(self.get_authorization_code(params))
            params.update(self.get_authorization_code(params))
        else:
            self.set_current_user(back_data.get('user_id'))
            self.set_parameters(params)

        return self.success(msg='Login Successfull.', data=params)


class LogoutHandler(BaseAuthHandler):
    """Log out."""

    @web.asynchronous
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        self.clear_all_cookies()
        self.success(msg='Logged out.', data=None)


class UserInfoHandler(BaseAuthHandler):

    @web.asynchronous
    @gen.coroutine
    @auth(
        a_3008=lambda user: user.permission & 1 == 1,
        b_3008=lambda user: user.permission & 2 == 2,
    )
    def post(self, *_args, **_kwargs):
        """Test POST."""
        res = self.get_parameters()
        print(res)
        args = self.parse_json_arguments(
            'first_name', 'last_name', 'industry')

        update_info = dict(
            user_id=res.user_id,
            first_name=args.first_name,
            last_name=args.last_name,
            company=args.company,
            title=args.title,
            country=args.country,
            avatar=args.avatar,
        )

        db_update_info = yield self.wait(db_task.update_account_info, kwargs=update_info)
        if db_update_info.get('status'):
            return self.fail(3999, data=db_update_info)

        db_users = yield self.wait(db_task.query_account, kwargs=dict(user_id=res.user_id))
        if db_users.get('status'):
            return self.fail(3999, data=db_users)

        back_data = db_users.get('data')
        params = self.bind_params(back_data)
        if O_O.auth_storage == 'JWT':
            params.update(self.get_authorization_code(params))
        else:
            self.set_current_user(back_data.get('user_id'))
            self.set_parameters(params)

        self.finish_with_json(params)


class RegisterHandler(BaseAuthHandler):

    @web.asynchronous
    @gen.coroutine
    def put(self, *_args, **_kwargs):
        """Test PUT."""

        args = self.parse_json_arguments(
            'email',
            'password',
            'first_name',
            'last_name',
            'company',
            'title',
            'country',
            'avatar',
            'industry',
        )
        if not pattern['email'].match(args.email):
            return self.fail(3032)
        if not pattern['password'].match(args.password):
            return self.fail(3031)

        invert_dict = dict(user_id=figure_id(), register_time=time.time(),
                           permission=0, register_ip=args.remote_ip, expire_time=0)
        args['password'] = security_encode(args.password)

        result = yield self.wait(db_task.query_account,  kwargs=dict(email=args.email))
        if result.get('status'):
            return self.fail(3999, data=result)

        back_data = result.get('data')
        if back_data:
            return self.fail(3004, data=dict(user_id=back_data.get('user_id')))

        args.update(invert_dict)
        print(args)
        result = yield self.wait(db_task.insert_account,  kwargs=args)
        if result.get('status'):
            return self.fail(3999, data=args)

        return self.success(msg='Register Successfull.')


ACCOUNT_ROUTES = [
    (r'/middle/authorization', UserCheckHandler),
    (r'/middle/logout', LogoutHandler),
    (r'/middle/register', RegisterHandler),
    (r'/middle/account', UserInfoHandler),
    # (r'/middle/reset-password', ResetPasswordHandler),
]
