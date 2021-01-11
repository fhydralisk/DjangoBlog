# coding=utf-8
from __future__ import unicode_literals

from base import serializers

from ..models import GuildMaterialsStock
from ..serializers import GuildMaterialsJournalWithNameSerializer, GuildMaterialsStockSerializer


class StockListSerializer(serializers.ReadonlySerializer):
    stocks = GuildMaterialsStockSerializer(many=True)


class JournalListApiSerializer(serializers.PagedListSerializerMixin):
    material = serializers.PrimaryKeyRelatedField(queryset=GuildMaterialsStock.objects.all(), allow_null=True)


class JournalListSerializer(serializers.ReadonlySerializer):
    journals = GuildMaterialsJournalWithNameSerializer(many=True)
