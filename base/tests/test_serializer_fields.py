from django.test import SimpleTestCase
from django.db import transaction
from base import serializers
from ..models.sms import AliSmsAPIMasterKey
from ..choices.sms_choice import sms_choice


class TestFieldSerializer(serializers.Serializer):
    id = serializers.TransactionAwarePrimaryKeyRelatedField(
        select_for_update=True, queryset=AliSmsAPIMasterKey.objects.all(), source='master_key'
    )


class TestTransactionAwarePrimaryKeyRelatedField(SimpleTestCase):
    allow_database_queries = True
    databases = '__all__'

    @classmethod
    def setUpClass(cls):
        cls.master_key = AliSmsAPIMasterKey.objects.create(
            app_key='foo',
            app_secret='bar',
            template_code='baz',
            sign_name='egg',
            usage=sms_choice.DISPATCHER_NOTIFY,
        )
        super(TestTransactionAwarePrimaryKeyRelatedField, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.master_key.delete()
        super(TestTransactionAwarePrimaryKeyRelatedField, cls).tearDownClass()

    def test_transaction_aware_pkrf_without_transaction(self):
        data = {
            'id': self.master_key.pk
        }

        serializer_without_transaction = TestFieldSerializer(data=data)
        serializer_without_transaction.is_valid(raise_exception=True)
        self.assertFalse(serializer_without_transaction.fields['id'].get_queryset().query.select_for_update)

    def test_transaction_aware_pkrf_with_transaction(self):
        data = {
            'id': self.master_key.pk
        }

        with transaction.atomic():
            serializer_with_transaction = TestFieldSerializer(data=data)
            serializer_with_transaction.is_valid(raise_exception=True)
            self.assertTrue(serializer_with_transaction.fields['id'].get_queryset().query.select_for_update)
