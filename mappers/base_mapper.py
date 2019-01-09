# coding:utf-8

from sqlalchemy.orm import Query, Session


class BaseMapper:
    """Base Mapper."""

    def __init__(self, session):
        if not isinstance(session, Session):
            raise ValueError(
                "session is not instance of sqlalchemy.orm.session.Session.")
        self.session = session
