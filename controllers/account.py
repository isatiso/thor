# coding:utf-8
"""Views Module."""

import time
from tornado import gen
from tornado.options import define

from config import CFG as O_O
from lib.web import BaseController, route, check_auth
from services.user_service import create_account, get_account_info


@route(r'/create')
class CreateAccount(BaseController):
    """Test index request handler."""

    @check_auth
    async def post(self, *_args, **_kwargs):
        """Get method of IndexHandler."""
        args = self.parse_json_arguments('username', 'phone', 'mail',
                                         'password')

        res = create_account(args.username, args.phone, args.mail,
                             args.password)
        self.success(res)


@route(r'/info')
class AccountInfo(BaseController):
    """Test index request handler."""

    async def get(self, *_args, **_kwargs):
        """Get method of IndexHandler."""
        args = self.parse_form_arguments('user_id')
        user_id = int(args.user_id)

        res = get_account_info(user_id)
        self.success(res)