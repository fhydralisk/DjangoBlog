import datetime
import pytz

from django.conf import settings


# TODO: Test and consider about time zone issue.

def datetime_to_timestamp(dt):
    if dt.tzinfo:
        epoch = datetime.datetime(1970, 1, 1, tzinfo=pytz.timezone('UTC'))
    else:
        epoch = datetime.datetime(1970, 1, 1)
    return int((dt - epoch).total_seconds())


def timestamp_to_datetime(ts, tzinfo=None):
    return datetime.datetime.fromtimestamp(ts, tz=tzinfo)


def forward_timezone(t):
    if settings.USE_TZ:
        if t is not None:
            return t.astimezone(pytz.timezone(settings.TIME_ZONE)).replace(tzinfo=pytz.timezone('UTC'))
        else:
            return None
    else:
        return t


def revert_timezone(t):
    if settings.USE_TZ:
        if t is not None:
            return pytz.timezone(settings.TIME_ZONE).localize(t.replace(tzinfo=None))
        else:
            return None
    else:
        return t
