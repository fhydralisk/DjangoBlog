"""
    Utilities None to 0
    Created by hangyu @ 12-13-2018
"""
import decimal
from django.db import models
from django.db.models.functions import Coalesce


def none_to_0(obj, is_decimal=False):
    if obj is None:
        return decimal.Decimal('0') if is_decimal else 0
    else:
        return obj


def field_none_to_0(func):
    return Coalesce(func, models.Value(0))
