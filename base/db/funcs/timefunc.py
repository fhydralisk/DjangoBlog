import six

from django.db import models
from django.conf import settings
from django.db.models.functions import datetime as datetime_funcs


class TimeAdd(models.Func):
    function = 'TIMESTAMPADD'
    template = 'CAST(%(function)s(MICROSECOND, %(duration_f)s, %(t_f)s) AS DATETIME)'

    def __init__(self, t_f, duration_f):
        super(TimeAdd, self).__init__(output_field=models.DateTimeField())
        self.t_f = self._parse_expressions(t_f)[0]
        if isinstance(duration_f, six.string_types):
            self.duration_f = self._parse_expressions(duration_f)[0]
        else:
            self.duration_f = duration_f

    def resolve_expression(self, query=None, allow_joins=True, reuse=None, summarize=False, for_save=False):
        c = self.copy()
        c.is_summary = summarize
        c.t_f = c.t_f.resolve_expression(query, allow_joins, reuse, summarize)
        c.duration_f = c.duration_f.resolve_expression(query, allow_joins, reuse, summarize)

        return c

    def as_sql(self, compiler, connection, function=None, template=None, arg_joiner=None, **extra_context):
        arg_sql_tf, arg_params_tf = compiler.compile(self.t_f)
        arg_sql_df, arg_params_df = compiler.compile(self.duration_f)
        params = arg_params_tf + arg_params_df
        data = {
            "function": self.function,
            "t_f": arg_sql_tf,
            "duration_f": arg_sql_df,
        }

        return self.template % data, params


INTERVAL_CANDIDATE = [
    'MICROSECOND',
    'SECOND',
    'MINUTE',
    'HOUR',
    'DAY',
    'WEEK',
    'MONTH',
    'QUARTER',
    'YEAR',
    'SECOND_MICROSECOND',
    'MINUTE_MICROSECOND',
    'MINUTE_SECOND',
    'HOUR_MICROSECOND',
    'HOUR_SECOND',
    'HOUR_MINUTE',
    'DAY_MICROSECOND',
    'DAY_SECOND',
    'DAY_MINUTE',
    'DAY_HOUR',
    'YEAR_MONTH',
]


class Interval(models.Expression):

    def __init__(self, value, unit):
        # type: (int, str) -> None
        self.value = value
        self.unit = str(unit).upper()
        if self.unit not in INTERVAL_CANDIDATE:
            raise ValueError(
                'unit must in %s' % ','.join(INTERVAL_CANDIDATE)
            )

        super(Interval, self).__init__()

    def as_sql(self, compiler, connection):
        # We here cannot return 'INTERVAL %s %s', [self.value, self.unit] because django will transform DAY into 'DAY'.
        return 'INTERVAL %%s %s' % self.unit, [self.value]


class DateFunc(models.Func):
    # TODO: Adapt to other databases rather than mysql
    template = '%(function)s(%(expressions)s)'
    operator = '+'

    def __init__(self, field, interval):
        if isinstance(field, models.Expression):
            pass
        elif isinstance(field, six.string_types):
            field = models.F(field)
        else:
            raise TypeError('field argument must be Expression')

        self.f = field

        if not isinstance(interval, Interval):
            raise TypeError('interval must be Interval')

        super(DateFunc, self).__init__(field, interval)

    def as_sql(self, compiler, connection, function=None, template=None, arg_joiner=None, **extra_context):
        if isinstance(self.f, DateFunc):
            return super(DateFunc, self).as_sql(
                compiler, connection, template='%(expressions)s', arg_joiner=' %s ' % self.operator,
            )
        else:
            return super(DateFunc, self).as_sql(compiler, connection, function, template, arg_joiner, **extra_context)


class DateAdd(DateFunc):
    function = 'DATE_ADD'
    operator = '+'


class DateDiff(DateFunc):
    function = 'DATE_DIFF'
    operator = '-'


class Now(models.Func):
    template = 'CURRENT_TIMESTAMP'

    def __init__(self, output_field=None, **extra):
        if output_field is None:
            output_field = models.fields.DateTimeField()
        super(Now, self).__init__(output_field=output_field, **extra)

    def as_mysql(self, compiler, connection):
        if settings.USE_TZ and settings.TIME_ZONE.upper() != 'UTC':
            return "CONVERT_TZ(%s, '%s', '%s')" % (self.template, settings.TIME_ZONE, 'UTC'), []
        else:
            return "CURRENT_TIMESTAMP()", []

    def as_postgresql(self, compiler, connection):
        # Postgres' CURRENT_TIMESTAMP means "the time at the start of the
        # transaction". We use STATEMENT_TIMESTAMP to be cross-compatible with
        # other databases.
        return self.as_sql(compiler, connection, template='STATEMENT_TIMESTAMP()')


class TruncInterval(models.Func):
    def __init__(self, field, interval, **extra):
        """
        Trunc Datetime with arbitrary interval.
        :param field: field to transform.
        :param interval: interval in seconds.
        :param extra: output_field, etc.
        """
        super(TruncInterval, self).__init__(field, interval=interval, **extra)

    def as_mysql(self, compiler, connection):
        template = "FROM_UNIXTIME(UNIX_TIMESTAMP(%(expressions)s) DIV %(interval)s * %(interval)s)"
        return super(TruncInterval, self).as_sql(compiler, connection, template=template)


class TruncArbitrary(object):
    agg_map = {
        'five_min': 300,
        'thirty_min': 1800,
        'three_hour': 10800,
    }

    def __new__(cls, field, kind, **kwargs):
        if kind in cls.agg_map:
            return TruncInterval(field, cls.agg_map[kind], **kwargs)
        else:
            return datetime_funcs.Trunc(field, kind, **kwargs)
