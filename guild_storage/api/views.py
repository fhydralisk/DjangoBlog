# coding=utf-8
from __future__ import unicode_literals

from base.views import WLAPIGenericView

from . import funcs
from . import serializers


class StockListView(WLAPIGenericView):
    http_method_names = ['get', 'options']
    FUNC_CLASS = funcs.StockListFunc
    RESULT_SERIALIZER = serializers.StockListSerializer


class JournalListView(WLAPIGenericView):
    http_method_names = ['get', 'options']
    API_SERIALIZER = serializers.JournalListApiSerializer
    FUNC_CLASS = funcs.JournalListFunc
    RESULT_SERIALIZER = serializers.JournalListSerializer
