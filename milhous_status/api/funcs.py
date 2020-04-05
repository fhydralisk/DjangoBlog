# coding=utf-8
from __future__ import unicode_literals


from base.funcs import AbstractFuncClass, PagedAbstractFuncClass
from ..models import MilhousHostStatistics, MilhousHost


class MilhousHostStateReportFunc(AbstractFuncClass):

    def run(self, host, usages, **kwargs):
        MilhousHostStatistics.objects.create(host=host, usages=usages)
        host.heartbeat()


class MilhousHostListFunc(PagedAbstractFuncClass):

    def get_paged_qs(self, **kwargs):
        return MilhousHost.objects.all(), "hosts", {}


class MilhousHostStatisticsListFunc(PagedAbstractFuncClass):

    def get_paged_qs(self, host, **kwargs):
        return MilhousHostStatistics.objects.filter(host=host).order_by('-report_date'), "statistics", {}
