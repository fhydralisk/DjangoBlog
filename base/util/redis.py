# coding=utf-8
from __future__ import unicode_literals

import redis
from django.conf import settings


pool = redis.ConnectionPool(**settings.REDIS_SERVER)


def get_redis():
    return redis.Redis(connection_pool=pool)
