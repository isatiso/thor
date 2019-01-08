# coding:utf-8
"""Lazor Database Module."""
import uuid
import enum
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (CHAR, BigInteger, Column, Enum, Integer, SmallInteger,
                        Text, String, Numeric, Float, TIMESTAMP)
from sqlalchemy import PrimaryKeyConstraint, Sequence, UniqueConstraint
from sqlalchemy import func, text

Base = declarative_base()


class Addition:

    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(
        TIMESTAMP,
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
                    elif isinstance(self.__dict__[key], datetime):
                        res[real_key] = int(self.__dict__[key].timestamp())
                    else:
                        res[real_key] = self.__dict__[key]

        return res