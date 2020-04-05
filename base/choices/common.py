# coding=UTF-8
from __future__ import unicode_literals
from base.util import field_choice


class _AcceptDenyChoice(field_choice.FieldChoice2):
    ACCEPT = field_choice.FieldChoiceSelection('accept', "同意")
    DENY = field_choice.FieldChoiceSelection('deny', "拒绝")


accept_deny_choice = _AcceptDenyChoice()


class _SerializerTypeChoice(field_choice.FieldChoice2):
    ST_API = field_choice.FieldChoiceSelection('api')
    ST_RESULT = field_choice.FieldChoiceSelection('result')


serializer_type_choice = _SerializerTypeChoice()
