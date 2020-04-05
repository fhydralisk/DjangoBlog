# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.timezone import now
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY

from .utils import get_session_engine, get_extended_session_model


def _get_backends(return_tuples=False):
    backends = []
    for backend_path in settings.AUTHENTICATION_BACKENDS:
        backend = import_string(backend_path)()
        backends.append((backend, backend_path) if return_tuples else backend)

    return backends


def get_or_create_session_from_request(request):
    """
    Get or create session from request.
    If no session in request, create one;
    If a extended session in request, create a new one to replace it;
    If a session without extended session in request, return it.
    :param request:
    :return:
    """
    session_engine = get_session_engine()
    session_model = get_extended_session_model()
    session_new = session_engine.SessionStore()
    session_new.cycle_key()
    session = getattr(request, 'session', session_new)

    try:
        ext_session = session_model.objects.get(session=session.session_key)
    except session_model.DoesNotExist:
        if session.session_key is None:
            return session_new
        else:
            return session
    else:
        return session_new


def login(request, user, **extra):
    # type: (HttpRequest, UserBase, dict) -> six.string_types
    """
    Login modified from django
    """
    session_auth_hash = ''
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    session = get_or_create_session_from_request(request)

    try:
        backend = user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                'You have multiple authentication backends configured and '
                'therefore must provide the `backend` argument or set the '
                '`backend` attribute on the user.'
            )

    session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    session[BACKEND_SESSION_KEY] = backend
    session[HASH_SESSION_KEY] = session_auth_hash
    session.update(extra)
    # saving into db or cache should be handled by session middleware.
    request.session = session

    user.last_login = now()
    user.save()
    # Rest framework use wrapped request that prevent us modifying the original request's session pointer.
    # So we check it here.
    if hasattr(request, '_request'):
        request._request.session = session
    return session.session_key


def logout(request):
    session = getattr(request, 'session', None)
    if session:
        session.flush()
