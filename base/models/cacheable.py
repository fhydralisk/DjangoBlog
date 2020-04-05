# coding=utf-8
from __future__ import unicode_literals

from ..util.db import transform_instance_to_dict


class CacheableModelMixin(object):

    @property
    def cache_object(self):
        return transform_instance_to_dict(self)
