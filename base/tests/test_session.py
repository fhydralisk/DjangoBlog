# coding=utf-8
from __future__ import unicode_literals

from django.test import override_settings
from django.http.request import HttpRequest
from django.contrib.auth import get_user_model, get_user

from ..session.utils import get_extended_session_model, get_session_engine
from ..session.login import login
from ..models.session import AbstractExtendedSession
from ..test_utils.testcases import WLTempModelTestCase


class DummyExtendedSession(AbstractExtendedSession):
    class Meta:
        app_label = WLTempModelTestCase.test_app_label


class BaseExtendedSessionTestCase(WLTempModelTestCase):
    test_session_key = '1a2b3c4d'
    temp_models = [DummyExtendedSession]

    @classmethod
    def setUpClass(cls):
        super(BaseExtendedSessionTestCase, cls).setUpClass()
        cls.override_settings = override_settings(EXTENDED_SESSION="test.DummyExtendedSession")
        cls.override_settings.enable()
        cls.session_model = get_extended_session_model()
        cls.session_engine = get_session_engine()

    @classmethod
    def tearDownClass(cls):
        cls.override_settings.disable()
        super(BaseExtendedSessionTestCase, cls).tearDownClass()

    def new_session(self, **extra):
        session = self.session_engine.SessionStore(self.test_session_key)
        session.update(extra)
        session.save(must_create=True)
        return session


class TestLogin(BaseExtendedSessionTestCase):

    def new_user(self):
        user_model = get_user_model()
        return user_model.objects.create_user(internal_name='Test', password='Test', is_active=True, role=0)

    def test_login_without_session(self):
        request = HttpRequest()
        user = self.new_user()
        session_key = login(request, user)
        self.assertEqual(session_key, request.session.session_key)
        self.assertEqual(user, get_user(request))

    def test_login_with_session_without_extension(self):
        session = self.new_session()
        request = HttpRequest()
        request.session = session
        user = self.new_user()
        session_key = login(request, user)
        self.assertEqual(session_key, session.session_key)
        self.assertEqual(user, get_user(request))

    def test_login_with_session_with_extension(self):
        session = self.new_session()
        self.session_model.objects.create(
            session=session.session_key
        )
        request = HttpRequest()
        request.session = session
        user = self.new_user()
        session_key = login(request, user)
        self.assertNotEqual(session_key, session.session_key)
        self.assertEqual(user, get_user(request))
