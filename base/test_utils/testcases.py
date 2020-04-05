import six

from django.test.testcases import TestCase
from django.db import connection, models
from django.apps import apps
from django.conf import settings
from django.test import override_settings
from .fixtures import AbstractFixtures
from .client import WLTestClient
from .json_schema import check_json_schema


class WLBaseTestCase(TestCase):

    fixture_mixins = None
    client_class = WLTestClient

    def _fixture_setup(self):
        super(WLBaseTestCase, self)._fixture_setup()

        if self.fixture_mixins:
            for fixture in self.fixture_mixins:  # type: AbstractFixtures
                fixture.setup()

    def assertHttpStatusEqual(self, response, status_code):
        self.assertEqual(response.status_code, status_code)

    def assertHttpStatusNotEqual(self, response, status_code):
        self.assertNotEqual(response.status_code, status_code)

    def assertResultEqual(self, response, result_code):
        self.assertEqual(self.get_response_data(response)['result'], result_code)

    def assertResultNotEqual(self, response, result_code):
        self.assertNotEqual(self.get_response_data(response)['result'], result_code)

    def assertHttpStatusOK(self, response):
        self.assertHttpStatusEqual(response, 200)

    def assertHttpStatusNotOK(self, response):
        self.assertHttpStatusNotEqual(response, 200)

    def assertResultOk(self, response):
        self.assertResultEqual(response, 200)

    def assertResultNotOk(self, response):
        self.assertResultNotEqual(response, 200)

    def assertPermissionCheckFail(self, response, permission, use_http_status=False):
        fail_code = permission.FAIL['code']
        if use_http_status:
            self.assertHttpStatusEqual(response, fail_code)
        else:
            self.assertResultEqual(response, fail_code)

    def assertResponseJsonLike(self, response, data_schema, check_type=True):
        data = self.get_response_data(response)
        data.pop('result', None)
        self.assertJsonLike(data, data_schema, check_type)

    def assertJsonLike(self, data, data_schema, check_type=True):
        errors = check_json_schema(data, data_schema, check_type=check_type)
        if errors:
            error_msg = '\n'.join(map(lambda (a, b): a + ' ' + b, errors))
            raise self.failureException(error_msg)

    def get_response_data(self, response):
        return response.json()['response']


class WLTempModelTestCase(WLBaseTestCase):

    temp_models = None
    test_app_label = 'test'

    @classmethod
    def setUpClass(cls):

        if cls.temp_models is not None:
            installed = settings.INSTALLED_APPS + [cls.test_app_label]
            cls.override_installed_apps = override_settings(INSTALLED_APPS=installed)
            cls.override_installed_apps.enable()
            with connection.schema_editor() as schema_editor:
                for model in cls.temp_models:
                    m = cls.get_real_model(model)
                    schema_editor.create_model(m)

        super(WLTempModelTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(WLTempModelTestCase, cls).tearDownClass()
        # We first tear down class, where the transaction is terminated.
        # So DDL in Transaction Error is cleared.

        if cls.temp_models is not None:
            with connection.schema_editor() as schema_editor:
                for model in reversed(cls.temp_models):
                    m = cls.get_real_model(model)
                    schema_editor.delete_model(m)
            cls.override_installed_apps.disable()

    @staticmethod
    def get_real_model(model):
        if isinstance(model, six.string_types):
            return apps.get_model(model)
        elif isinstance(model, (list, tuple)):
            return apps.get_model(*model)
        elif issubclass(model, models.Model):
            return model
        else:
            raise TypeError('model must be instance of Model')
