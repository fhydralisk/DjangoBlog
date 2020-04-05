# coding=utf-8
from __future__ import unicode_literals

from django.utils.timezone import localtime
from django.db import models


class NumberGenerateMixin(object):

    number_field = 'number'

    @classmethod
    def generate_number(cls, prefix):
        return prefix + localtime().strftime('%Y%m%d%H%M') + cls.get_number_postfix()

    @classmethod
    def get_number_postfix(cls):
        try:
            last_instance = cls.objects.filter(**{
                "%s__isnull" % cls.number_field: False
            }).latest('created_date')
            # FIXME: in concurrent case, this is not correct.
            return "%04d" % (
                (int(getattr(last_instance, cls.number_field)[-4:]) + 1) % 1000
            )
        except (models.ObjectDoesNotExist, ValueError, TypeError):
            return "0001"
