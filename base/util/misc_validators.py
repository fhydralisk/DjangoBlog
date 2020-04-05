"""
Regex validator for phone number, email, etc.

Created by Hangyu Fan, May 6, 2018

Last modified: May 7, 2018
"""
from __future__ import unicode_literals

import six
import re
from django.conf import settings
from django.utils.module_loading import import_string
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError


@deconstructible
class AbstractValidator(object):
    message = 'Enter a valid value.'
    code = 'invalid'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def validate(self, vstr):
        raise NotImplementedError

    def __call__(self, value):
        if not self.validate(value):
            raise ValidationError(self.message, code=self.code)


@deconstructible
class RegexAbstractValidator(AbstractValidator):

    REGEX_PATTERN = r''

    def __init__(self, **kwargs):
        if isinstance(self.REGEX_PATTERN, basestring):
            self.reg = re.compile(self.REGEX_PATTERN)
        super(RegexAbstractValidator, self).__init__(**kwargs)

    def regex_validate(self, vstr):
        if not isinstance(vstr, six.string_types):
            return False

        return self.reg.match(vstr) is not None

    def validate(self, vstr):
        return self.regex_validate(vstr)


@deconstructible
class PNValidator(RegexAbstractValidator):
    REGEX_PATTERN = r'^((13[0-9])|(14[0-9])|(15([0-9]))|(18[0-9])|(17[0-9])|(19[0-9]))\d{8}$'


@deconstructible
class DummyValidator(AbstractValidator):
    """
    Dummy Validator always pass validations
    """
    def validate(self, vstr):
        return True


class PlateNumberValidator(RegexAbstractValidator):
    REGEX_PATTERN = ur'[\u4e00-\u9fa5][A-Z][A-Z0-9]{5}'

    def regex_validate(self, vstr):
        if not isinstance(vstr, six.string_types):
            return False

        if six.PY2:
            if not isinstance(vstr, unicode):
                vstr = vstr.decode('utf-8')
        elif six.PY3:
            # Untested
            if not isinstance(vstr, str):
                vstr = vstr.decode('utf-8')

        return self.reg.match(vstr) is not None


class IDCardNumberValidator(RegexAbstractValidator):
    REGEX_PATTERN = r'^[1-9]\d{7}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}$|^[1-9]\d{5}[1-9]\d{3}' \
                    r'((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])\d{3}([0-9]|X)$'


class ValidatorManager(object):
    def __init__(self):
        self._validators = {
            e["NAME"]: import_string(e["CLASS"])(**(e["ARGS"] if "ARGS" in e else {}))
            for e in settings.STRING_VALIDATORS
        }

    def validate(self, vstr, vname):
        if vname not in self._validators:
            raise KeyError("validator not exist")
        else:
            return self._validators[vname].validate(vstr)

    def get_validator(self, vname):
        if vname not in self._validators:
            raise KeyError("validator not exist")
        else:
            return self._validators[vname]


validators = ValidatorManager()
