import re
import json
from json import JSONDecodeError
import inspect


class Arguments(dict):
    """Class to manage arguments of a requests."""

    def __init__(self, params):
        if isinstance(params, dict):
            super().__init__(params)
        elif not params:
            super().__init__(dict())
        else:
            raise TypeError(
                f"Arguments data should be a 'dict' not {type(params)}.")

    def __getattr__(self, name):
        attr = self.get(name)
        if isinstance(attr, dict):
            attr = self.__class__(attr)
        return attr

    def __setattr__(self, name, value):
        raise PermissionError('Can not set attribute to <class Arguments>.')

    def insert(self, key, value):
        """Add a variable to args."""
        if key in self:
            raise PermissionError(f'Key {key} is already exists.')
        else:
            self[key] = value


def check_params(func):
    def inner(*args, **kwargs):
        for name, value in inspect.signature(func).parameters.items():
            if value.kind == value.VAR_KEYWORD:
                continue
            if value.kind == value.VAR_POSITIONAL:
                continue

            if kwargs.get(name) is None:
                if (value.default != value.empty):
                    kwargs[name] = value.default
                else:
                    raise PermissionError(f'Missing key <"{name}">.')

            if (value.annotation == value.empty):
                if (name not in kwargs):
                    raise PermissionError(f'Annotation of key <"{name}"> is not exists.')

            if not isinstance(kwargs[name], value.annotation):
                raise PermissionError(f'Type of key <"{name}"> is not right.')

        return kwargs

    return inner


@check_params
def test_check(a: list = 2, **kwargs):
    return kwargs


if __name__ == '__main__':
    res = test_check(a = ("1",), test=3)
    print(res)
