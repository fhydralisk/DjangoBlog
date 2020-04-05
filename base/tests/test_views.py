# coding=utf-8
from __future__ import unicode_literals

import mock

from django.test.utils import override_settings
from django.conf.urls import url
from django_fsm import TransitionNotAllowed
from rest_framework.exceptions import ValidationError

from ..util import filters
from ..test_utils.testcases import WLBaseTestCase
from ..views import WLAPIGenericView, WLModelMethodView
from ..funcs import AbstractFuncClass, PagedAbstractFuncClass, ModelMethodFunc, AbstractPermission
from .. import serializers
from ..models import MiniprogramAppSecret
from .test_session import BaseExtendedSessionTestCase


# Dummy Testing
class DummyFunc(AbstractFuncClass):
    def run(self, request, user, serializer, **kwargs):
        pass


class TestView(WLAPIGenericView):
    http_method_names = ['get', 'post', 'options']
    FUNC_CLASS = DummyFunc


# Filter Testing
class FilterApiSerializer(serializers.PageApiSerializer):
    pass


class FilterModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiniprogramAppSecret
        fields = '__all__'


class FilterResultSerializer(serializers.ReadonlySerializer):
    models = FilterModelSerializer(many=True)


class Filter(filters.FilterSet):
    appid = filters.CharFilter(lookup_expr='contains')
    appid_choice = filters.ChoiceFilter(choices=(
        (1, 'appid1'),
        (2, 'appid2'),
    ), field_name='appid', lookup_expr='contains')

    class Meta:
        model = MiniprogramAppSecret
        fields = ('appid', 'appid_choice')


# ModelMethod Testing
class MiniprogramAppSecretProxy(MiniprogramAppSecret):
    def test_method_without_args(self, change_app_id):
        self.appid = change_app_id
        self.save()
        return self.id

    def test_method_with_args(self, secret):
        self.appsecret = secret
        self.save()

    def method_not_allowed(self):
        pass

    def test_method_raise(self):
        raise TransitionNotAllowed()

    class Meta:
        proxy = True


class TestArgSerializer(serializers.ApiSerializer):
    secret = serializers.CharField()

    def validate(self, attrs):
        if not attrs['secret'].startswith('key'):
            raise ValidationError(detail={'secret': '必须以key开头'})
        return attrs


class TestResultSerializer(serializers.ReadonlySerializer):
    id = serializers.IntegerField()
    secret = serializers.CharField()


class TestPermission(AbstractPermission):
    def check_permission(self, instance, **kwargs):
        return instance is not None


class TestModelMethodFunc(ModelMethodFunc):
    PERMISSIONS = [
        TestPermission()
    ]

    model_class = MiniprogramAppSecretProxy
    allow_methods = [
        'test_method_without_args',
        'test_method_with_args',
        'method_not_exists',
        'test_method_raise',
    ]

    def pre_test_method_without_args(self, **kwargs):
        return {
            "change_app_id": 'test_app_id'
        }

    def post_test_method_without_args(self, instance, result, **kwargs):
        return {
            'id': str(result),
            'secret': instance.appsecret,
            'other': '123',
        }


class TestModelMethodView(WLModelMethodView):
    RESULT_SERIALIZER = {
        'test_method_without_args': TestResultSerializer
    }
    METHOD_ARG_SERIALIZER = {
        'test_method_with_args': TestArgSerializer
    }
    FUNC_CLASS = TestModelMethodFunc


class FilterFunc(PagedAbstractFuncClass):
    filter_set_class = Filter

    def get_paged_qs(self, **kwargs):
        return MiniprogramAppSecret.objects.all(), "models", {}


class FilterView(WLAPIGenericView):
    API_SERIALIZER = FilterApiSerializer
    FUNC_CLASS = FilterFunc
    RESULT_SERIALIZER = FilterResultSerializer


urlpatterns = [
    url(r'^dummy/', TestView.as_view(), name='dummy_view'),
    url(r'^filter/', FilterView.as_view(), name='filter_view'),
    url(r'^method/', TestModelMethodView.as_view(), name='method_view'),
]


@override_settings(ROOT_URLCONF=__name__)
class TestWLAPIGenericViewSession(BaseExtendedSessionTestCase):

    view_name = 'dummy_view'

    def test_check_session_without_session(self):
        response = self.client.get(self.view_name)
        self.assertHttpStatusOK(response)
        self.assertResultOk(response)

    def test_check_session_with_session_no_extension(self):
        session = self.new_session()
        response = self.client.get(self.view_name, data={'user_sid': session.session_key})
        self.assertHttpStatusOK(response)
        self.assertResultOk(response)

    def test_check_session_with_valid_extension(self):
        session = self.new_session()
        self.session_model.objects.create(
            session=session.session_key,
            is_valid=True,
        )
        response = self.client.get(self.view_name, data={'user_sid': session.session_key})
        self.assertHttpStatusOK(response)
        self.assertResultOk(response)

    def test_check_session_with_invalid_extension(self):
        session = self.new_session()
        self.session_model.objects.create(
            session=session.session_key,
            is_valid=False,
        )
        response = self.client.get(self.view_name, data={'user_sid': session.session_key})
        self.assertHttpStatusOK(response)
        self.assertResultEqual(response, 404)

    def test_check_session_kicked(self):
        session = self.new_session(kicked=True)
        response = self.client.get(self.view_name, data={'user_sid': session.session_key})
        self.assertHttpStatusOK(response)
        self.assertResultEqual(response, 499)

    def test_view_do_not_check_session(self):
        with mock.patch.object(TestView, 'CHECK_SESSION', False):
            session = self.new_session(kicked=True)
            response = self.client.get(self.view_name, data={'user_sid': session.session_key})
            self.assertHttpStatusOK(response)
            self.assertResultEqual(response, 200)


@override_settings(ROOT_URLCONF=__name__)
class TestDjangoFilterFuncView(WLBaseTestCase):
    view_name = 'filter_view'

    @classmethod
    def setUpTestData(cls):
        MiniprogramAppSecret.objects.create(
            appid='appid1',
            appsecret='appsecret1',
        )
        MiniprogramAppSecret.objects.create(
            appid='appid11',
            appsecret='appsecret1',
        )
        MiniprogramAppSecret.objects.create(
            appid='appid2',
            appsecret='appsecret1',
        )
        super(TestDjangoFilterFuncView, cls).setUpTestData()

    def test_no_filter(self):
        response = self.client.get(path=self.view_name)
        self.assertEqual(3, len(response.json()['response']['models']))

    def test_filter(self):
        response = self.client.get(path=self.view_name, data={'appid': 'appid1'})
        self.assertEqual(2, len(response.json()['response']['models']))

    def test_choice_filter(self):
        response = self.client.get(path=self.view_name, data={'appid_choice': '1'})
        self.assertEqual(2, len(response.json()['response']['models']))

    def test_bad_filter(self):
        response = self.client.get(path=self.view_name, data={'appid_choice': '3'})
        self.assertHttpStatusOK(response)
        self.assertResultEqual(response, 400)


@override_settings(ROOT_URLCONF=__name__)
class TestDjangoMethodView(WLBaseTestCase):
    view_name = 'method_view'

    def setUp(self):
        self.test_data = MiniprogramAppSecret.objects.create(
            appid='appid1',
            appsecret='appsecret1',
        )

    def test_no_args(self):
        response = self.client.post(path=self.view_name, data={
            "data": {
                'id': self.test_data.id,
                'method': 'test_method_without_args',
                'args': {},
            }
        })

        self.test_data.refresh_from_db()

        self.assertHttpStatusOK(response)
        self.assertResultOk(response)
        self.assertResponseJsonLike(response, {
            "id": 1,
            "secret": "secret",
        })
        self.assertEqual(
            self.test_data.id, response.json()['response']['id']
        )
        self.assertEqual(
            self.test_data.appsecret, response.json()['response']['secret']
        )
        self.assertEqual(
            'test_app_id', self.test_data.appid
        )

    def test_with_args(self):
        new_key = 'key123'
        response = self.client.post(path=self.view_name, data={
            "data": {
                'id': self.test_data.id,
                'method': 'test_method_with_args',
                'args': {
                    'secret': new_key
                }
            }
        })
        self.assertHttpStatusOK(response)
        self.assertResultOk(response)
        self.test_data.refresh_from_db()
        self.assertEqual(new_key, self.test_data.appsecret)

    def test_with_args_validate_fail(self):
        new_key = '123'
        response = self.client.post(path=self.view_name, data={
            "data": {
                'id': self.test_data.id,
                'method': 'test_method_with_args',
                'args': {
                    'secret': new_key
                }
            }
        })
        self.assertHttpStatusOK(response)
        self.assertResultEqual(response, 400)

    def test_not_allowed_method(self):
        response = self.client.post(path=self.view_name, data={
            "data": {
                'id': self.test_data.id,
                'method': 'method_not_allowed',
                'args': {}
            }
        })
        self.assertHttpStatusOK(response)
        self.assertResultEqual(response, 400)

    def test_not_exist_method(self):
        response = self.client.post(path=self.view_name, data={
            "data": {
                'id': self.test_data.id,
                'method': 'method_not_exists',
                'args': {}
            }
        })
        self.assertHttpStatusOK(response)
        self.assertResultEqual(response, 400)

    def test_non_exist_model(self):
        response = self.client.post(path=self.view_name, data={
            "data": {
                'id': 100000,
                'method': 'test_method_without_args',
                'args': {}
            }
        })
        self.assertHttpStatusOK(response)
        self.assertResultEqual(response, 400)

    def test_exception_map(self):
        response = self.client.post(path=self.view_name, data={
            "data": {
                'id': self.test_data.id,
                'method': 'test_method_raise',
                'args': {}
            }
        })
        self.assertHttpStatusOK(response)
        self.assertResultEqual(response, 453)
