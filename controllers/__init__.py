# coding:utf-8

import importlib
import pkgutil

module_dict = dict()


def load_controllers():
    for m in pkgutil.iter_modules(__spec__.submodule_search_locations):
        module_dict[m.name] = importlib.import_module('controllers.' + m.name)
