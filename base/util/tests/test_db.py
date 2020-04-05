from django.test import TestCase
from ...models.miniprog_app import MiniprogramAppSecret
from ..db import append_filter_to_qs


class TestAppendFilter(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.m1 = MiniprogramAppSecret.objects.create(
            appid='123',
            appsecret='456',
        )
        cls.m2 = MiniprogramAppSecret.objects.create(
            appid='456',
            appsecret='123',
        )
        cls.m3 = MiniprogramAppSecret.objects.create(
            appid='123',
            appsecret='678',
        )
        cls.m4 = MiniprogramAppSecret.objects.create(
            appid='456',
            appsecret='789',
        )
        super(TestAppendFilter, cls).setUpTestData()

    def testAppendFilter(self):
        qs = MiniprogramAppSecret.objects.all()
        filters_list = [
            [
                ('appid', '123'),
            ],
            [
                ('-appid', '123'),
            ],
            [
                ('appid', '123'),
                ('appsecret', '456'),
            ],
            [
                (('appid', 'appsecret'), '123'),
            ],
            [
                (('appid', '-appsecret'), '123'),
            ]
        ]
        result_list = [
            [self.m1, self.m3],
            [self.m2, self.m4],
            [self.m1],
            [self.m1, self.m2, self.m3],
            [self.m1, self.m3, self.m4],
        ]
        for index, (fil, result) in enumerate(zip(filters_list, result_list)):
            print("Testing append_filter_to_qs: %d" % index)
            qs_test = append_filter_to_qs(qs, fil)
            self.assertListEqual(list(qs_test), result)

    def testAppendFilterConditional(self):
        qs = MiniprogramAppSecret.objects.all()
        filters_list = [
            [
                ('appid', '123', True),
            ],
            [
                ('-appid', '123', False),
            ],
            [
                ('appid', '123', None),
                ('appsecret', '456', True),
            ],
            [
                (('appid', 'appsecret'), '123', False),
            ],
            [
                (('appid', '-appsecret'), '123', False),
            ]
        ]
        result_list = [
            [self.m1, self.m3],
            [self.m1, self.m3],
            [self.m1],
            [self.m4],
            [self.m2],
        ]
        for index, (fil, result) in enumerate(zip(filters_list, result_list)):
            print("Testing conditional append_filter_to_qs: %d" % index)
            qs_test = append_filter_to_qs(qs, fil)
            self.assertListEqual(list(qs_test), result)

