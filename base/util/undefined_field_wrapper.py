"""
A utility makes DRF field to be aware of "undefined" values.
"""
from rest_framework.serializers import Field


def undefined_field_wrapper(field_class, undefined_keywords=None):

    def to_internal_value(self, data):
        if data in undefined_keywords:
            return None
        else:
            return field_class.to_internal_value(self, data)

    if not issubclass(field_class, Field):
        raise ValueError("{} is not drf field.".format(field_class.__class__.__name__))

    if undefined_keywords is None:
        undefined_keywords = ['undefined']

    new_class = type(
        'UndefinedWrapped%s' % field_class.__class__.__name__,
        (field_class, ),
        {
            "to_internal_value": to_internal_value,
        })

    return new_class
