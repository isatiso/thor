from functools import wraps
import time
from pprint import pprint

import inspect

def get_sess():
    global sess
    sess = time.time()
    # print(globals())
    return sess


def test_dec(func):
    """test"""
    pprint(func.__globals__)
    print(func.__doc__)
    # print(inspect.isfunction(func))
    # print()

    # @wraps(func)
    def wrapper(*args, **kwargs):
        sess = time.time()
        func.__dict__['sess'] = sess
        if inspect.isfunction(func):
            res = func(*args, sess=sess, **kwargs)
        # sess = func.__globals__['sess']
        # print(sess)
        return res

    return wrapper
