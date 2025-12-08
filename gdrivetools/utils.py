# -*- encoding: utf-8 -*-
'''
@Time     :   2025/11/19 17:51:56
@Author   :   QuYue
@File     :   utils.py
@Email    :   quyue1541@gmail.com
@Desc:    :   utils
'''


#%% Import Packages
import math

#%% AttrDict
class AttrDict(dict):
    """
    Dictionary that supports attribute-style access and
    recursively wraps nested dicts/lists into AttrDict.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.update(*args, **kwargs)

    @classmethod
    def _wrap(cls, value):
        if isinstance(value, dict) and not isinstance(value, AttrDict):
            return cls(value)
        elif isinstance(value, list):
            return [cls._wrap(v) for v in value]
        else:
            return value

    def __setitem__(self, key, value):
        super().__setitem__(key, self._wrap(value))

    def update(self, *args, **kwargs):
        other = dict(*args, **kwargs)
        for k, v in other.items():
            self[k] = v

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            return super().__setattr__(key, value)
        self[key] = value

    def __delattr__(self, key):
        if key.startswith("_"):
            return super().__delattr__(key)
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


#%% Size
def human_size(n, precision=2):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    if n <= 0:
        return "0 B"
    i = int(math.floor(math.log(n, 1024)))
    p = math.pow(1024, i)
    s = round(n / p, precision)
    return f"{s} {units[i]}"


