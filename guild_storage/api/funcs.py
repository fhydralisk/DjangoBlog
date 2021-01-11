# coding=utf-8
from __future__ import unicode_literals

from django.db.models import Q
from base.funcs import AbstractFuncClass, PagedAbstractFuncClass
from ..models import GuildMaterialsStock, GuildMaterialsJournal


class StockListFunc(AbstractFuncClass):

    def run(self, request, user, serializer, **kwargs):
        return {
            "stocks": GuildMaterialsStock.objects.all()
        }


class JournalListFunc(PagedAbstractFuncClass):

    def get_paged_qs(self, material, **kwargs):
        if material:
            qs = GuildMaterialsJournal.objects.filter(Q(material_input=material) | Q(material_output=material))
        else:
            qs = GuildMaterialsJournal.objects.all()

        return qs, "journals", {}
