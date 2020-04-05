# coding=UTF-8
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from base.util import field_choice


class _SMSChoice(field_choice.FieldChoice2):
    VALIDATION = field_choice.FieldChoiceSelection(0, "验证短信 - B/C", alias='validation')
    BOOKKEEPING_C = field_choice.FieldChoiceSelection(1, "记账短信 - C", alias='bookkeeping_c')
    LOGGING_STATUS = field_choice.FieldChoiceSelection(2, "致命错误提示", alias='logging_status')
    DISPATCHER_NOTIFY = field_choice.FieldChoiceSelection(3, "运营派单提醒", alias='dispatcher_notify')


sms_choice = _SMSChoice()
