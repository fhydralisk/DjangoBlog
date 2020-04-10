# coding=utf-8
from __future__ import unicode_literals


from base.views import WLAPIGenericView

from . import funcs
from . import serializers


class MilhousHostListView(WLAPIGenericView):
    http_method_names = ['get', 'options']
    FUNC_CLASS = funcs.MilhousHostListFunc
    RESULT_SERIALIZER = serializers.MilhousHostListResultSerializer


class MilhousHostStatisticsListView(WLAPIGenericView):
    http_method_names = ['get', 'options']
    API_SERIALIZER = serializers.MilhousHostStatisticsApiSerializer
    FUNC_CLASS = funcs.MilhousHostStatisticsListFunc
    RESULT_SERIALIZER = serializers.MilhousHostStatisticsListResultSerializer


class MilhousHostStatisticsReportView(WLAPIGenericView):
    http_method_names = ['post', 'options']
    API_SERIALIZER = serializers.MilhousHostStateUploadApiSerializer
    FUNC_CLASS = funcs.MilhousHostStateReportFunc


class MilhousCharacterPingView(WLAPIGenericView):
    http_method_names = ['get', 'options']
    API_SERIALIZER = serializers.MilhousCharacterPingApiSerializer
    FUNC_CLASS = funcs.MilhousCharacterPingFunc
