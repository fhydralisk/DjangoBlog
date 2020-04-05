# coding=utf-8
from __future__ import unicode_literals

from base import serializers
from ..models import MilhousHost, HostMachineType, MilhousCharacter


class HostRelatedApiSerializer(serializers.ApiSerializer):
    host = serializers.SlugRelatedField(queryset=MilhousHost.objects.all(), slug_field='name')


class MilhousHostStateSerializer(serializers.ReadonlySerializer):
    usages = serializers.JSONField()
    report_date = serializers.TimestampField(read_only=True)


class MilhousHostStateUploadApiSerializer(HostRelatedApiSerializer, MilhousHostStateSerializer):
    pass


class MilhousHostStatisticsApiSerializer(HostRelatedApiSerializer):
    pass


class MilhousHostStatisticsListResultSerializer(serializers.ReadonlySerializer):
    statistics = MilhousHostStateSerializer(many=True)


class MilhousCharacterSerializer(serializers.ModelSerializer):

    class Meta:
        model = MilhousCharacter
        fields = (
            'character',
            'expire',
            'photo',
        )


class MilhousHostTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = HostMachineType
        fields = (
            'name',
            'icon',
        )


class MilhousHostSerializer(serializers.ModelSerializer):

    host_type = MilhousHostTypeSerializer()
    characters = MilhousHostTypeSerializer(many=True)

    class Meta:
        model = MilhousHost
        fields = (
            'id',
            'name',
            'host_desc',
            'host_type',
            'characters',
            'is_alive',
        )


class MilhousHostListResultSerializer(serializers.PagedListSerializerMixin):
    hosts = MilhousHostSerializer(many=True)
