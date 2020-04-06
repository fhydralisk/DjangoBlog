"""
Abstract SMS
"""

import logging
from django.conf import settings
from django.utils.module_loading import import_string
from base.choices.sms_choice import sms_choice


logger = logging.getLogger(__name__)


class AbstractSMS(object):

    def __init__(self, usage, exclude=None):
        self.usage = usage
        self._exclude = set()
        if exclude is not None:
            self.set_exclude(exclude)

    def should_send(self, pn):
        return pn not in self._exclude

    def set_exclude(self, exclude):
        if isinstance(exclude, (set, list, tuple)):
            self._exclude = set(exclude)
        else:
            raise TypeError('exclude arg mst be a set, list or tuple')

    def send_sms(self, pn, context):
        raise NotImplementedError


class DummySMS(AbstractSMS):

    def send_sms(self, pn, context):
        pass


class ConsolePrintSMS(AbstractSMS):

    def send_sms(self, pn, context):
        if self.should_send(pn):
            print("sending to {} with context {}".format(pn, context))
        else:
            print("pn is in exclude.")


class SMSManager(object):
    def __init__(self):
        self.sms_clz = DummySMS
        self.sms_clz_name = settings.SMS
        self._sms = None
        self.refresh()

    def refresh(self):
        try:
            self.sms_clz = import_string(settings.SMS)
        except ImportError:
            logger.error('Error while loading SMS:{}. Fall back to DummySMS'.format(settings.SMS))
            self.sms_clz = DummySMS

        # Build SMS List for specified usage
        self._sms = {
            usage: self.sms_clz(
                usage=usage,
            ) for usage in sms_choice.get_choices()
        }

    @property
    def sms(self):
        if self.sms_clz_name != settings.SMS:
            self.refresh()  # For unittests.

        return dict(self._sms)

    def __getitem__(self, item):
        return self.sms[item]


sms_manager = SMSManager()
