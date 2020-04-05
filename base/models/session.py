# coding=utf-8
"""
Abstract Extended Session Model

Written by Hangyu Fan. 7.21.2019
"""
from __future__ import unicode_literals

from django.db import models
from ..session.utils import get_session_engine


class AbstractExtendedSession(models.Model):

    session = models.CharField(max_length=128, unique=True)
    is_valid = models.BooleanField(verbose_name="是否有效", default=False)

    @property
    def session_key(self):
        return self.session

    def get_session(self):
        session_engine = get_session_engine()
        return session_engine.SessionStore(self.session_key)

    class Meta:
        abstract = True
