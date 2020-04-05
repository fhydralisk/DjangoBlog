from rest_framework import serializers


class UserPasswordLoginApiSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ValidateViaSMSApiSerializer(serializers.Serializer):
    pn = serializers.CharField()


class ResetPasswordApiSerializer(serializers.Serializer):
    sid = serializers.CharField()
    pn = serializers.CharField()
    vcode = serializers.CharField()
    new_password = serializers.CharField()
