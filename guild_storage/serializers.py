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

    material_input_name = serializers.ReadOnlyField(source='material_input.name')
    material_output_name = serializers.ReadOnlyField(source='material_output.name')

    class Meta(GuildMaterialsJournalSerializer.Meta):
        fields = GuildMaterialsJournalSerializer.Meta.fields + (
            'material_input_name',
            'material_output_name',
        )
