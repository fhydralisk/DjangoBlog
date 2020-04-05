# coding=utf-8
from __future__ import unicode_literals

import six
import json

from django.http.request import HttpRequest
from django.shortcuts import reverse
from django.test.client import Client
from django.utils.encoding import force_bytes

from ..session.utils import get_session_engine


class WLTestClient(Client):
    def __init__(self, *args, **kwargs):
        super(WLTestClient, self).__init__(*args, **kwargs)
        self._user_sid = None
        self._logged_in_user = None

    def _login(self, user, backend=None):
        from django.contrib.auth import login
        engine = get_session_engine()

        # Create a fake request to store login details.
        request = HttpRequest()

        if self.session:
            request.session = self.session
        else:
            request.session = engine.SessionStore()
        login(request, user, backend)

        # Save the session values.
        request.session.save()

        self._user_sid = request.session.session_key
        self._logged_in_user = user

    def login_and_request(self, user, backend=None, method='get', **extra):
        self.force_login(user, backend)
        return getattr(self, method)(**extra)

    @staticmethod
    def try_reverse(path):
        if not path.startswith('/'):
            return reverse(path)
        else:
            return path

    def post(self, path, data=None, content_type='application/json',
             follow=False, secure=False, **extra):

        return super(WLTestClient, self).post(
            path=path,
            data=self._try_json_encode(data),
            content_type=content_type,
            follow=follow,
            secure=secure,
            **extra
        )

    def put(self, path, data=None, content_type='application/json',
            follow=False, secure=False, **extra):

        return super(WLTestClient, self).put(
            path=path,
            data=self._try_json_encode(data),
            content_type=content_type,
            follow=follow,
            secure=secure,
            **extra
        )

    def patch(self, path, data=None, content_type='application/json',
              follow=False, secure=False, **extra):

        return super(WLTestClient, self).patch(
            path=path,
            data=self._try_json_encode(data),
            content_type=content_type,
            follow=follow,
            secure=secure,
            **extra
        )

    @staticmethod
    def _try_json_encode(data):
        if isinstance(data, dict):
            data = json.dumps(data)
        return data

    def generic(self, method, path, data='',
                content_type='application/octet-stream', secure=False,
                **extra):
        path = self.try_reverse(path)

        if self._user_sid is not None:
            if b'QUERY_STRING' in extra:
                extra[b'QUERY_STRING'] += force_bytes('&user_sid=%s' % self._user_sid)
            else:
                extra[b'QUERY_STRING'] = force_bytes('user_sid=%s' % self._user_sid)

        if isinstance(data, dict):
            content_type = 'application/json'
            data = json.dumps(data)

        return super(WLTestClient, self).generic(
            method=method, path=path, data=data, content_type=content_type, secure=secure, **extra
        )

    @property
    def session(self):
        if self._user_sid is not None:
            engine = get_session_engine()
            return engine.SessionStore(self._user_sid)
        else:
            return super(WLTestClient, self).session
