"""
Utility - set if not null
"""


def set_if_not_null(o, **kwargs):
    c = 0

    for attr, obj in kwargs.items():
        if obj is not None:
            setattr(o, attr, obj)
            c += 1

    return c
