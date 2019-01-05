# coding:utf-8
import time
from mappers import UserQuery
from lib.dao import transaction, dict_of


@transaction
def create_account(username, phone, mail, password, **kwargs):
    a = time.time()
    sess = kwargs.get('sess')
    print(time.time() - a)
    a = time.time()
    user_query = UserQuery(sess)
    print(time.time() - a)
    a = time.time()
    res = user_query.insert_user(username, phone, mail, password)
    print(time.time() - a)
    a = time.time()
    sess.commit()
    print(time.time() - a)
    return res


@transaction
def get_account_info(user_id, **kwargs):
    user_query = UserQuery(kwargs.get('sess'))
    user_info = user_query.query_user_by_id(user_id)

    return dict_of(user_info)
