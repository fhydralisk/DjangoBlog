
from django.utils.module_loading import import_module
from django.conf import settings
from django.apps import apps


class ExtendedSessionNotSet(Exception):
    pass


def get_session_engine():
    return import_module(settings.SESSION_ENGINE)


def get_extended_session_model():
    try:
        return apps.get_model(settings.EXTENDED_SESSION)
    except AttributeError:
        raise ExtendedSessionNotSet()
