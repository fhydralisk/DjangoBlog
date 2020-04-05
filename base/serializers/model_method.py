from rest_framework import serializers


class ModelMethodSerializer(serializers.Serializer):
    id = serializers.CharField()
    args = serializers.JSONField()
    method = serializers.CharField()
