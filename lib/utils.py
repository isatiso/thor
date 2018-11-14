
import socket
import struct
import time
import random
import string
import io
import base64

from functools import wraps
from config import CFG as O_O
from cryptography.fernet import Fernet


def security_encode(password):
    """ password encode 

    b'111111'
    to
    b'gAAAAABbaWqToP3KzqHiGkhLPsSUzf-qlTtBribri4qWB713LZ10iEehhBifu7fQZ7hb7OPNVJD3oIooTKvbM5Fr-dE-dY-62w=='
    """

    if isinstance(password, str):
        password = str.encode(password)
    cipher_suite = Fernet(O_O.security_key)
    return bytes.decode(cipher_suite.encrypt(password))


def security_decode(password):
    """ password decode 
    b'gAAAAABbaWqToP3KzqHiGkhLPsSUzf-qlTtBribri4qWB713LZ10iEehhBifu7fQZ7hb7OPNVJD3oIooTKvbM5Fr-dE-dY-62w=='
    to
    b'111111'
    """
    if isinstance(password, str):
        password = str.encode(password)
    cipher_suite = Fernet(O_O.security_key)

    try:
        return bytes.decode(cipher_suite.decrypt(password))
    except:
        return ''


def figure_id(namespace='0000'):
    """Creat file id"""
    timep = hex(int(time.time() * 1000))[2:]
    rands = f'{random.randint(0, 65536):04x}'
    return f'{namespace}-{timep[4:8]}-{timep[:4]}-{rands}-{timep[8:]}'


def extract_anywhere_keys(result, options, **kwargs):
    """
    extract object to dict by oiptions fields

    :param result:
        A : extract Object
    :type result:
        `object`
    :param options:
            extract to fields , get all fields and attribute on Object.
    :type options:
        `list`
    :return:
        A : object convert to dict by options
    :rtype:
        :class:`dict`

    """
    back_data = dict()
    for key in options:
        if isinstance(result, dict):
            back_data[key] = result.get(key)
        else:
            back_data[key] = result.__dict__.get(key) or getattr(result, key)

    for key in kwargs:
        if isinstance(result, dict):
            back_data[key] = result.get(key, kwargs.get(key))
        else:
            back_data[key] = result.__dict__.get(
                key, kwargs.get(key)) or getattr(result, key, kwargs.get(key))

    # for key in result.__dict__:
    #     if not options or key in options:
    #         back_data[key] = result.__dict__.get(key) or getattr(result, key)
    return back_data
