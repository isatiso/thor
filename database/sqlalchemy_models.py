# coding:utf-8
"""Lazor Database Module."""
import uuid
import enum
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (CHAR, BigInteger, Column, Enum, Integer, SmallInteger,
                        Text, String, Numeric, Float, TIMESTAMP)
from sqlalchemy import PrimaryKeyConstraint, Sequence, UniqueConstraint
from sqlalchemy import text

from .sqlalchemy_base import Base, Addition


class User(Base, Addition):
    """User Model."""
    __tablename__ = 'user'

    user_id = Column(Integer)
    mail = Column(String(120), index=True)
    phone = Column(String(20), index=True)
    username = Column(String(10), index=True)
    password = Column(CHAR(32))

    is_super = Column(SmallInteger, server_default=text('0'))
    active = Column(SmallInteger, server_default=text('0'))

    __table_args__ = (
        PrimaryKeyConstraint('user_id'),
        {
            'mysql_engine': 'InnoDB'
        },
    )
