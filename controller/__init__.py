# coding:utf-8

import importlib
import pkgutil

module_dict = dict()


def load_subcontroller():
    for m in pkgutil.iter_modules(__spec__.submodule_search_locations):
        module_dict[m.name] = importlib.import_module('controller.' + m.name)
