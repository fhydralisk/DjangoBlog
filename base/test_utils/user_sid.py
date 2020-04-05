# coding=utf-8
from django.test.testcases import Client

from base.util.db import append_filter_to_qs
from usersys.models import UserBase


class EmptyUserBaseException(Exception):

    def __init__(self, exception_msg):
        self.exception_msg = exception_msg

    def __str__(self):
        return "EmptyUserBaseException:{}".format(self.exception_msg)


class TestUserSid(object):
    client = Client()

    def __init__(self, internal_name=None, is_staff=None, is_superuser=None, role=None):
        self.internal_name = internal_name
        self.role = role
        self.is_staff = is_staff
        self.is_superuser = is_superuser

    def get_user_sid(self):
        users = UserBase.objects.all()
        filters = [
            ('internal_name', self.internal_name),
            ('role', self.role),
            ('is_staff', self.is_staff),
            ('is_superuser', self.is_superuser),
        ]
        users = append_filter_to_qs(users, filters, True)
        if users.count() == 0:
            raise EmptyUserBaseException('Not filtered to users...')
        self.client.force_login(users.first())
        return self.client.session.session_key

    def get_superuser_sid(self):
        users = UserBase.objects.filter(is_superuser=True)
        if users.count() == 0:
            raise EmptyUserBaseException('Not filtered to superuser...')
        self.client.force_login(users.first())
        return self.client.session.session_key

    def get_is_staff_user_sid(self):
        users = UserBase.objects.filter(is_staff=True)
        if users.count() == 0:
            raise EmptyUserBaseException('Not filtered to is_staff user...')
        self.client.force_login(users.first())
        return self.client.session.session_key
