# coding:utf-8

from sqlalchemy.orm import Query

from database.sqlalchemy_models import User
from .base_mapper import BaseMapper


class UserMapper(BaseMapper):
    """User Query Factory."""

    def query_user_by_id(self, user_id, **kwargs):
        query = Query(User, self.session).filter(User.user_id == user_id)
        return query.first()

    def query_user_by_name(self, username, **kwargs):
        query = Query(User, self.session).filter(User.username == username)
        return query.first()

    def query_user_by_phone(self, phone, **kwargs):
        query = Query(User, self.session).filter(User.phone == phone)
        return query.first()

    def insert_user(self, username, phone, mail, password, **kwargs):
        user = User(
            username=username, phone=phone, mail=mail, password=password)
        self.session.add(user)
        return