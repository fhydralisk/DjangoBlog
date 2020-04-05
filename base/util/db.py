"""
Database utilities
"""
import six
import logging
from functools import reduce, partial
from django.db.models import Model, QuerySet, Q, Manager
from django.db.models.signals import post_save, post_delete


default_logger = logging.getLogger(__name__)


def update_instance_from_dict(instance, dic, save=False):
    for k, v in dic.items():
        # Related Field cannot be found via hasattr(instance, k)
        if hasattr(instance, k) or hasattr(instance.__class__, k):
            if isinstance(v, dict):
                update_instance_from_dict(getattr(instance, k), v, save)
            else:
                setattr(instance, k, v)

    if save:
        instance.save()


def transform_instance_to_dict(instance):
    fields = instance._meta.fields
    instance_dict = {field.get_attname(): getattr(instance, field.get_attname()) for field in fields}
    return instance_dict


class Condition(object):
    def __init__(self, condition):
        self.condition = condition


def _transform_to_q(key, value):
    if key.startswith('-'):
        return ~Q(**{key[1:]: value})
    else:
        return Q(**{key: value})


def condition_based_filter(qs, exclude, condition):
    # type: (QuerySet, bool, Condition) -> callable
    if condition is None or condition.condition:
        if exclude:
            return getattr(qs, 'exclude')
        else:
            return getattr(qs, 'filter')
    else:
        if exclude:
            return getattr(qs, 'filter')
        else:
            return getattr(qs, 'exclude')


def _append_filter(qs, filter_key, filter_value, condition):
    # type: (QuerySet, (str, list, tuple, set), object, Condition) -> QuerySet
    if isinstance(filter_key, six.string_types):
        if filter_key.startswith('-'):
            qs = condition_based_filter(qs, True, condition)(**{filter_key[1:]: filter_value})
        else:
            qs = condition_based_filter(qs, False, condition)(**{filter_key: filter_value})
    elif isinstance(filter_key, (list, tuple, set)):
        qs = condition_based_filter(qs, False, condition)(
            reduce(
                lambda a, b: a | b,
                map(partial(_transform_to_q, value=filter_value), filter_key)
            )
        )
    else:
        raise TypeError('filter_key must be str or iterable. got %s.' % filter_key.__class__.__name__)

    return qs


def append_filter_to_qs(qs, filter_list, remove_none_filter=False):

    for e in filter_list:
        if len(e) == 2:
            k, v = e
            condition = None
            if v is None and remove_none_filter:
                continue
        elif len(e) == 3:
            k, v, condition = e
            if condition is None:
                continue
            condition = Condition(condition)
        else:
            raise ValueError('Element in filter list must be Tuple2 or Tuple3')

        qs = _append_filter(qs, k, v, condition)

    return qs


class LastLineConfigManager(object):

    CLZ_MODEL = None
    _instance = None
    cls_logger = None

    def __init__(self, reload_callback=None, logger=None):
        if not issubclass(self.CLZ_MODEL, Model):
            raise TypeError
        if callable(reload_callback):
            self.reload_callback = reload_callback
        elif reload_callback is not None:
            raise TypeError("reload callback must be None or callable")
        else:
            self.reload_callback = None

        if isinstance(logger, logging.Logger):
            self.cls_logger = logger
        elif logger is None:
            if self.cls_logger is None:
                self.cls_logger = default_logger
            else:
                if not isinstance(self.cls_logger, logging.Logger):
                    raise TypeError("logger must be a Logger class.")
        else:
            raise TypeError("logger must be a Logger class.")

        post_save.connect(self.reload, sender=self.CLZ_MODEL)
        post_delete.connect(self.reload, sender=self.CLZ_MODEL)

    def reload(self, **kwargs):
        self.cls_logger.info("%s is reloading due to signals" % self.CLZ_MODEL.__name__)
        self.do_load()
        if self.reload_callback is not None:
            self.reload_callback(self._instance)

    def do_load(self):
        try:
            self._instance = self.extra_filter(self.CLZ_MODEL.objects).last()
        except NotImplementedError:
            self._instance = self.CLZ_MODEL.objects.last()

    def extra_filter(self, qs):
        # type: (QuerySet) -> QuerySet
        raise NotImplementedError

    @property
    def instance(self):
        if self._instance is None:
            self.do_load()

        return self._instance


class UsedObjectManager(Manager):
    def get_queryset(self):
        return super(UsedObjectManager, self).get_queryset().filter(in_use=True)


class GetSuperQuerysetMixin(object):

    @classmethod
    def queryset_class(cls):
        return cls._queryset_class
