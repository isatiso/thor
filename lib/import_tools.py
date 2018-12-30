# coding:utf-8
import os
from os.path import join, abspath, dirname
import importlib
import traceback


def load(app: str):

    controller_name = f'app.{app}.controller'
    _load_subpackage(controller_name)


def _load_subpackage(package_name: str):

    package_path = os.sep.join(package_name.split('.'))

    caller_name = traceback.extract_stack(limit=3)[0].filename
    package_path = join(abspath(dirname(caller_name)), package_path)
    package_name += '.'

    for filename in os.listdir(package_path):
        filename = os.path.splitext(filename)[0]
        importlib.import_module(package_name + filename)
