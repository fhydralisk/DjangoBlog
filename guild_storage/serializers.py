# coding=utf-8
from __future__ import unicode_literals

from base import serializers

from .models import GuildMaterialsStock, GuildMaterialsJournal


class GuildMaterialsStockSerializer(serializers.DynamicFieldsMixin, serializers.ModelSerializer):

    class Meta:
        model = GuildMaterialsStock
        fields = (
            'name',
            'stock',
            'unit',
            'image',
            'order',
        )


class GuildMaterialsJournalSerializer(serializers.DynamicFieldsMixin, serializers.ModelSerializer):

    operate_date = serializers.TimestampField()

    class Meta:
        model = GuildMaterialsJournal
        fields = (
            'material_input',
            'amount_input',
            'material_output',
            'amount_output',
            'input_from',
            'output_to',
            'operate_date',
            'comment',
        )


class GuildMaterialsJournalWithNameSerializer(GuildMaterialsJournalSerializer):

    material_input = GuildMaterialsStockSerializer()
    material_output = GuildMaterialsStockSerializer()
