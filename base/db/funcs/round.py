from django.db import models


class Round(models.Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, %(decimal_places)d)'

    def __init__(self, field, decimal_places):
        super(Round, self).__init__(field, decimal_places=int(decimal_places))
