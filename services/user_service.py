# coding:utf-8
import time
from mappers import UserMapper
from lib.dao import transaction, dict_of


@transaction
def create_account(username, phone, mail, password, **kwargs):
    sess = kwargs.get('sess')
    user_query = UserMapper(sess)
    res = user_query.insert_user(username, phone, mail, password)
    sess.commit()

    return res


@transaction
def get_account_info(user_id, **kwargs):
    sess = kwargs.get('sess')
    user_query = UserMapper(sess)
    user_info = user_query.query_user_by_id(user_id)

    return dict_of(user_info)
