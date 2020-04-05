from rest_framework import serializers


class WrappedPhoneNumberField(serializers.CharField):

    def to_representation(self, value):
        value = super(WrappedPhoneNumberField, self).to_representation(value)
        if value is not None and len(value) >= 7:
            return value[0:3] + "****" + value[-4:]
        else:
            return value
