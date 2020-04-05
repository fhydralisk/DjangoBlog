# coding=utf-8
from __future__ import unicode_literals


class OriginalModelSignalMixin(object):

    def _perform_method(self, method, *args, **kwargs):
        original_class = self.__class__
        base_class = self._meta.concrete_model
        if original_class is base_class:
            return getattr(super(OriginalModelSignalMixin, self), method)(*args, **kwargs)
        else:
            self.__class__ = base_class
            try:
                result = getattr(self, method)(*args, **kwargs)
            finally:
                self.__class__ = original_class
            return result

    def save(self, *args, **kwargs):
        return self._perform_method('save', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._perform_method('delete', *args, **kwargs)
