# coding=utf-8
from __future__ import unicode_literals

import pytz
import six

from functools import reduce
from django.conf import settings
from django.db.models import Q
from django.forms.widgets import NumberInput, Input
from django.forms.fields import DateTimeField, MultipleChoiceField
from django_filters import *  # NOQA
from django_filters.constants import EMPTY_VALUES
from django_filters.fields import Lookup, ModelMultipleChoiceField

from .timestamp import timestamp_to_datetime


class TimestampField(DateTimeField):
    widget = NumberInput
    input_formats = ['%s', ]  # we do not use this variable.

    def strptime(self, value, format):
        return timestamp_to_datetime(float(value), tzinfo=self.tzinfo)

    @property
    def tzinfo(self):
        if settings.USE_TZ:
            return pytz.timezone(settings.TIME_ZONE)
        else:
            return None


class TimestampFilter(Filter):
    field_class = TimestampField


class FieldChoiceFilterMixin(object):
    def __init__(self, *args, **kwargs):
        self.field_choice = kwargs.pop('field_choice')
        self.use_alias = kwargs.pop('use_alias', True)
        if self.use_alias:
            choices = self.field_choice.alias_choice.choice
        else:
            choices = self.field_choice.choice
        super(FieldChoiceFilterMixin, self).__init__(*args, choices=choices, **kwargs)

    def get_real_value(self, value):
        if not value or value == self.null_value:
            return None
        if self.use_alias:
            return self.field_choice.get_alias_real_data(value)
        else:
            return value


class FieldChoiceFilter(FieldChoiceFilterMixin, ChoiceFilter):

    def filter(self, qs, value):
        return super(FieldChoiceFilter, self).filter(qs, self.get_real_value(value))


class MultipleFieldChoiceFilter(FieldChoiceFilterMixin, MultipleChoiceFilter):

    def filter(self, qs, value):
        value = map(lambda v: self.get_real_value(v), value)
        return super(MultipleFieldChoiceFilter, self).filter(qs, value)


class CommaSplitWidget(Input):
    splitter = ','

    def value_from_datadict(self, data, files, name):
        try:
            values = data.getlist(name)
            if values:
                values = reduce(lambda e1, e2: e1 + e2, map(lambda x: x.split(','), values))
            return values
        except AttributeError:
            values = data.get(name)
            if values is None:
                return None
            else:
                return values.split(self.splitter)


class CommaSplitMultipleChoiceField(MultipleChoiceField):
    widget = CommaSplitWidget


class CommaSplitMultipleFieldChoiceFilter(MultipleFieldChoiceFilter):
    field_class = CommaSplitMultipleChoiceField


class CommaSplitModelMultipleChoiceField(ModelMultipleChoiceField):
    widget = CommaSplitWidget


class CommaSplitModelMultipleChoiceFilter(ModelMultipleChoiceFilter):
    field_class = CommaSplitModelMultipleChoiceField


class MultipleFieldFilter(Filter):
    def __init__(self, sub_filter_class, field_names, conjoined=True, **kwargs):
        super(MultipleFieldFilter, self).__init__(**kwargs)
        kwargs.pop('field_name', None)
        self.field_class = sub_filter_class.field_class
        self.field_names = field_names
        self.conjoined = conjoined
        self.sub_filters = [
            sub_filter_class(field_name=field_name, **kwargs)
            for field_name in field_names
        ]

    def filter(self, qs, value):
        if self.conjoined:
            for sub_filter in self.sub_filters:
                qs = sub_filter.filter(qs, value)
        else:
            if isinstance(value, Lookup):
                lookup = six.text_type(value.lookup_type)
                value = value.value
            else:
                lookup = self.lookup_expr
            if value in EMPTY_VALUES:
                return qs
            if self.distinct:
                qs = qs.distinct()

            q = Q()
            for sub_filter in self.sub_filters:
                q = q | Q(**{'%s__%s' % (sub_filter.field_name, lookup): value})
            qs = self.get_method(qs)(q)
        return qs
