# coding:utf-8
"""Lazor Database Module."""
import uuid
import enum

from sqlalchemy import (CHAR, BigInteger, Column, Enum, Integer, SmallInteger,
                        Text, String, Numeric, Float, TIMESTAMP)
from sqlalchemy import PrimaryKeyConstraint, Sequence, UniqueConstraint
from sqlalchemy import func, text

from .model_base import BASE


class User(BASE):
    """User Model."""
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    mail = Column(String(120), comment='用户邮箱', index=True)
    user_name = Column(String(10), comment='用户名', index=True)
    password = Column(CHAR(32), comment='密码')

    is_super = Column(SmallInteger, default=0, nullable=False)
    active = Column(SmallInteger, default=0, nullable=False)

    __table_args__ = ({'mysql_engine': 'InnoDB'}, )
