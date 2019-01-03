# coding:utf-8
"""Base Module."""

import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import (CHAR, BigInteger, Enum, Integer, SmallInteger,
                              Text, String, Numeric, Float, TIMESTAMP)

from sqlalchemy import func, text, Column
BASE = declarative_base()

BASE.created_at = Column(
    TIMESTAMP, comment='创建时间', server_default=text('CURRENT_TIMESTAMP'))
BASE.updated_at = Column(
    TIMESTAMP,
    comment='更新时间',
    server_default=text('CURRENT_TIMESTAMP  ON UPDATE CURRENT_TIMESTAMP'))


def to_dict(self, *options, **alias):
    res = dict()
    for key in options:
        alias[key] = None

    for key in self.__dict__:
        if not alias or key in alias:
            if not key.startswith('_'):
                if isinstance(alias.get(key), str):
                    real_key = alias[key]
                else:
                    real_key = key
                if isinstance(self.__dict__[key], enum.Enum):
                    res[real_key] = self.__dict__[key].name
                else:
                    res[real_key] = self.__dict__[key]

    return res


BASE.to_dict = to_dict
