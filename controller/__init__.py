# coding:utf-8

import importlib
import pkgutil


def load_subcontroller():
    for m in pkgutil.iter_modules(__spec__.submodule_search_locations):
        importlib.import_module('controller.' + m.name)
