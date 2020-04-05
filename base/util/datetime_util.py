import pytz

from dateutil import relativedelta
from django.conf import settings
from . import field_choice


class _RoundTimeMethodChoice(field_choice.FieldChoice2):
    RM_DAY = field_choice.FieldChoiceSelection('day')
    RM_WEEK = field_choice.FieldChoiceSelection('week')
    RM_MONTH = field_choice.FieldChoiceSelection('month')
    RM_YEAR = field_choice.FieldChoiceSelection('year')


round_time_method_choice = _RoundTimeMethodChoice()


def round_time(t, method):
    # get start and end of this week
    if method == round_time_method_choice.RM_WEEK:
        s = t + relativedelta.relativedelta(hour=0, minute=0, second=0, weekday=relativedelta.MO(-1))
        e = t + relativedelta.relativedelta(hour=23, minute=59, second=59, weekday=relativedelta.SU(0))
    elif method == round_time_method_choice.RM_MONTH:
        s = t + relativedelta.relativedelta(hour=0, minute=0, second=0, day=1)
        e = t + relativedelta.relativedelta(hour=23, minute=59, second=59, day=1, months=1, days=-1)
    elif method == round_time_method_choice.RM_DAY:
        s = t + relativedelta.relativedelta(hour=0, minute=0, second=0)
        e = t + relativedelta.relativedelta(hour=23, minute=59, second=59)
    elif method == round_time_method_choice.RM_YEAR:
        s = t + relativedelta.relativedelta(hour=0, minute=0, second=0, day=1, month=1)
        e = t + relativedelta.relativedelta(hour=23, minute=59, second=59, day=31, month=12)
    else:
        raise ValueError("Invalid method")
    return s, e


def localized_time(t):
    if settings.USE_TZ:
        if t.tzinfo is None:
            pytz.timezone(settings.TIME_ZONE).localize(t)
        else:
            return t.astimezone(pytz.timezone(settings.TIME_ZONE))
    else:
        return t