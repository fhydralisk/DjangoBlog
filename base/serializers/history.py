import copy
from rest_framework import serializers
from .fields.timestamp import TimestampField


class HistoryRecordMixin(serializers.ModelSerializer):
    history_date = TimestampField()
    history_change_reason = serializers.CharField()

    def get_fields(self):
        fields_map = super(HistoryRecordMixin, self).get_fields()
        declared_fields = copy.deepcopy(self._declared_fields)
        fields_map['history_date'] = declared_fields['history_date']
        fields_map['history_change_reason'] = declared_fields['history_change_reason']

        return fields_map
