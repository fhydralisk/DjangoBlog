from django.core.exceptions import ValidationError

from ..test_utils.testcases import WLBaseTestCase
from ..models import AliSmsAPIMasterKey
from ..choices.sms_choice import sms_choice
from ..util import filters


class AliSmsFilter(filters.FilterSet):

    start_time = filters.TimestampFilter('upload_date', lookup_expr='gte')
    end_time = filters.TimestampFilter('upload_date', lookup_expr='lt')
    usage = filters.FieldChoiceFilter(field_choice=sms_choice)
    usages = filters.CommaSplitMultipleFieldChoiceFilter(field_choice=sms_choice, field_name='usage')
    usage_list = filters.MultipleFieldChoiceFilter(field_choice=sms_choice, field_name='usage')
    key_or_secret = filters.MultipleFieldFilter(
        field_names=['app_key', 'app_secret'],
        sub_filter_class=filters.CharFilter,
        lookup_expr='contains',
        conjoined=False
    )
    key_and_secret = filters.MultipleFieldFilter(
        field_names=['app_key', 'app_secret'],
        sub_filter_class=filters.CharFilter,
        lookup_expr='contains',
        conjoined=True,
    )

    class Meta:
        model = AliSmsAPIMasterKey
        strict = filters.STRICTNESS.RAISE_VALIDATION_ERROR
        fields = [
            'app_key',
            'start_time',
            'end_time',
            'usage',
            'usages',
            'usage_list',
            'key_or_secret',
        ]


class TestFilter(WLBaseTestCase):

    @classmethod
    def change_upload_date(cls, obj, date):
        obj.upload_date = date
        obj.save()

    @classmethod
    def setUpTestData(cls):
        obj = AliSmsAPIMasterKey.objects.create(
            app_key='appkey1',
            app_secret='sec11',
            template_code='foo',
            sign_name='bar',
            usage=sms_choice.VALIDATION,
        )
        cls.change_upload_date(obj, "2019-03-01T00:00:00+08:00")
        obj = AliSmsAPIMasterKey.objects.create(
            app_key='appkey2',
            app_secret='sec12',
            template_code='foo',
            sign_name='bar',
            usage=sms_choice.BOOKKEEPING_C,
        )
        cls.change_upload_date(obj, "2019-04-01T00:00:00+08:00")
        obj = AliSmsAPIMasterKey.objects.create(
            app_key='appkey3',
            app_secret='sec13',
            template_code='foo',
            sign_name='bar',
            usage=sms_choice.LOGGING_STATUS,
        )
        cls.change_upload_date(obj, "2019-05-01T00:00:00+08:00")
        obj = AliSmsAPIMasterKey.objects.create(
            app_key='appkey4',
            app_secret='sec4',
            template_code='foo',
            sign_name='bar',
            usage=sms_choice.DISPATCHER_NOTIFY,
        )
        cls.change_upload_date(obj, "2019-06-01T00:00:00+08:00")

        super(TestFilter, cls).setUpTestData()

    def test_full_time(self):
        # 1551369600 is 2019-3-1 0:0:0 BJ
        hit_time = 1551369600
        start_time = hit_time - 1
        end_time = hit_time + 1
        filter_ = AliSmsFilter(
            data={'start_time': str(start_time), "end_time": str(end_time)},
            queryset=AliSmsAPIMasterKey.objects.all())
        qs = filter_.qs
        self.assertEqual(1, qs.count())
        self.assertEqual(sms_choice.VALIDATION, qs.get().usage)
        self.assertTrue(filter_.form.is_valid)

    def test_left_time(self):
        # 1551369600 is 2019-3-1 0:0:0 BJ
        hit_time = 1551369600
        start_time = hit_time - 1
        end_time = hit_time + 1
        qs = AliSmsFilter(
            data={'start_time': str(start_time)},
            queryset=AliSmsAPIMasterKey.objects.all()).qs
        self.assertEqual(4, qs.count())

    def test_right_time(self):
        # 1551369600 is 2019-3-1 0:0:0 BJ
        hit_time = 1551369600
        start_time = hit_time - 1
        end_time = hit_time + 1
        qs = AliSmsFilter(
            data={"end_time": str(end_time)},
            queryset=AliSmsAPIMasterKey.objects.all()).qs
        self.assertEqual(1, qs.count())

    def test_choice(self):
        qs = AliSmsFilter(
            data={"usage": "validation"}, queryset=AliSmsAPIMasterKey.objects.all()
        ).qs
        self.assertEqual(1, qs.count())
        self.assertEqual(sms_choice.VALIDATION, qs.get().usage)

    def test_split_choice(self):
        qs = AliSmsFilter(
            data={"usages": "validation,bookkeeping_c"}, queryset=AliSmsAPIMasterKey.objects.all()
        ).qs
        self.assertEqual(2, qs.count())

    def test_invalid_choice(self):
        with self.assertRaises(ValidationError):
            _ = AliSmsFilter(
                data={"usage": "invalid"}, queryset=AliSmsAPIMasterKey.objects.all()
            ).qs

    def test_multiple_choice(self):
        qs = AliSmsFilter(
            data={"usage_list": ["validation", "bookkeeping_c"]}, queryset=AliSmsAPIMasterKey.objects.all()
        ).qs
        self.assertEqual(2, qs.count())

    def test_multiple_field_choice_and(self):
        qs = AliSmsFilter(
            data={"key_and_secret": "1"},
            queryset=AliSmsAPIMasterKey.objects.all()
        ).qs
        self.assertEqual(1, qs.count())

    def test_multiple_field_choice_or(self):
        qs = AliSmsFilter(
            data={"key_or_secret": "1"},
            queryset=AliSmsAPIMasterKey.objects.all()
        ).qs
        self.assertEqual(3, qs.count())

    def test_comma_split_multiple_model_choice(self):
        pass
