# coding=UTF-8
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from base.util import field_choice


class _SMSChoice(field_choice.FieldChoice2):
    HOST_STATE = field_choice.FieldChoiceSelection(1, "主机状态变化", alias='host_state')


sms_choice = _SMSChoice()
