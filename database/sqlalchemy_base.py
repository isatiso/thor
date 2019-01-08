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
