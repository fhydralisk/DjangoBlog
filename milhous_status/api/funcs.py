# coding=utf-8
from __future__ import unicode_literals


from base.funcs import AbstractFuncClass, PagedAbstractFuncClass
from ..models import MilhousHostStatistics, MilhousHost, MilhousCharacter


class MilhousHostStateReportFunc(AbstractFuncClass):

    def run(self, host, usages, **kwargs):
        MilhousHostStatistics.objects.create(host=host, usages=usages)
        host.heartbeat()


class MilhousHostListFunc(PagedAbstractFuncClass):

    def get_paged_qs(self, **kwargs):
        return MilhousHost.objects.all().order_by('-id'), "hosts", {}


class MilhousHostStatisticsListFunc(PagedAbstractFuncClass):

    def get_paged_qs(self, host, **kwargs):
        return MilhousHostStatistics.objects.filter(host=host).order_by('-id'), "statistics", {}


class MilhousCharacterPingFunc(AbstractFuncClass):

    def run(self, character, **kwargs):
        # type: (MilhousCharacter, any) -> None
        character.heartbeat()
