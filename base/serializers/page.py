from rest_framework import serializers
from .api import ApiSerializer, ReadonlySerializer


class PageApiSerializer(ApiSerializer):
    pass


class PagedListSerializerMixin(ReadonlySerializer):
    n_pages = serializers.IntegerField()
    count = serializers.IntegerField()
