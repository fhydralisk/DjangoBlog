# coding=utf-8


def fallback_if_none(obj, default):
    if obj is None:
        return default
    else:
        return obj
