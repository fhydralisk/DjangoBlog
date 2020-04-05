from django.db import transaction
from rest_framework import serializers


class TransactionAwarePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.select_for_update = kwargs.pop('select_for_update', False)
        self.nowait = kwargs.pop('nowait', False)
        self.skip_locked = kwargs.pop('skip_locked', False)
        super(TransactionAwarePrimaryKeyRelatedField, self).__init__(**kwargs)

    def get_queryset(self):
        queryset = super(TransactionAwarePrimaryKeyRelatedField, self).get_queryset()
        if self.select_for_update and not transaction.get_autocommit():
            queryset = queryset.select_for_update(nowait=self.nowait, skip_locked=self.skip_locked)

        return queryset
