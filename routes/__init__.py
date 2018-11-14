# coding:utf-8
"""Routes Module."""

from .index import INDEX_ROUTES
from handlers import ACCOUNT_ROUTES

ROUTES = sum([
    INDEX_ROUTES,
    ACCOUNT_ROUTES
], [])
