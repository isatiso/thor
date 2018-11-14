# coding:utf-8
"""useragent Database Module"""
import enum

from sqlalchemy import (CHAR, Column, Enum, Integer, SmallInteger, String,
                        Text, UniqueConstraint, ForeignKey, Table, Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

BASE = declarative_base()


def to_dict(self, options=None):
    res = dict()
    for key in self.__dict__:
        if not options or key in options:
            if not key.startswith('_'):
                if isinstance(self.__dict__[key], enum.Enum):
                    res[key] = self.__dict__[key].name
                else:
                    res[key] = self.__dict__[key]
    return res


# turn to dict
BASE.to_dict = to_dict
# turn to string
BASE.__repr__ = lambda self: self.__tablename__ + ' => ' + str(self.to_dict())


class User(BASE):
    """User model"""
    __tablename__ = 'user'

    user_id = Column(CHAR(36), primary_key=True)
    email = Column(String(255), index=True)
    password = Column(String(255))
    register_time = Column(Integer, default=0, index=True)
    permission = Column(SmallInteger, nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    company = Column(String(255))
    title = Column(String(255))
    country = Column(CHAR(40))
    avatar = Column(CHAR(180))
    register_ip = Column(CHAR(17), default='0.0.0.0')
    industry = Column(String(255))
    login_inc = Column(Integer, default=0, index=True)
    expire_time = Column(Integer, nullable=False, default=0, index=True)

    __table_args__ = ({'mysql_engine': 'InnoDB'}, )
