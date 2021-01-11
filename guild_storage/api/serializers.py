# coding=utf-8
from __future__ import unicode_literals

from base import serializers

from ..models import GuildMaterialsStock
from ..serializers import GuildMaterialsJournalWithNameSerializer, GuildMaterialsStockSerializer


class StockListSerializer(serializers.ReadonlySerializer):
    stocks = GuildMaterialsStockSerializer(many=True)


class JournalListApiSerializer(serializers.PageApiSerializer):
    material = serializers.PrimaryKeyRelatedField(
        queryset=GuildMaterialsStock.objects.all(),
        allow_null=True,
        default=None
    )


class JournalListSerializer(serializers.PagedListSerializerMixin):
    journals = GuildMaterialsJournalWithNameSerializer(many=True)
