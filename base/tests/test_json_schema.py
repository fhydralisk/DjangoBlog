from unittest import TestCase

from ..test_utils.json_schema import check_json_schema


class TestJsonSchema(TestCase):
    def test_check_without_type(self):
        errors = dict(check_json_schema(
            {'k1': 'v1', 'ke': 've'},
            {'k1': 1, 'k2': 2},
            check_type=False
        ))

        self.assertNotIn('k1', errors)
        self.assertIn('k2', errors)
        self.assertIn('ke', errors)

    def test_check_with_type(self):
        errors = dict(check_json_schema(
            {'k1': 'v1', 'ke': 've', 'k2': []},
            {'k1': 1, 'k2': None},
            check_type=True
        ))

        self.assertIn('k1', errors)
        self.assertIn('ke', errors)
        self.assertNotIn('k2', errors)

    def test_check_with_dict(self):
        errors = dict(
            check_json_schema(
                {
                    'k1': 'v1', 'k2': {
                        'k21': 1,
                        'k22': {
                            'k221': 'test',
                            'k222': 'foo',
                        },
                        'k23': 0,
                    },
                    'k3': 'error',
                    'k4': {},
                },
                {
                    'k1': 'str', 'k2': {
                        'k21': 0,
                        'k22': {
                            'k221': 'str',
                            'k222': 0,
                        }
                    },
                    'k3': {},
                    'k4': {},
                },
                check_type=True,
            )
        )

        self.assertIn('k2.k23', errors)
        self.assertIn('k2.k22.k222', errors)
        self.assertIn('k3', errors)
        self.assertNotIn('k4', errors)

    def test_check_with_list(self):
        errors = dict(
            check_json_schema(
                {
                    'k1': 'v1', 'k2': {
                        'k21': 1,
                        'k22': [0, 1, 'error'],
                        'k23': [
                            {
                                'k231': 1
                            },
                            {
                                'k232': 'error'
                            },
                            {
                                'k231': 'error'
                            }
                        ],
                        'k24': [
                            [0, 1, 2],
                            ['err1', 'err2', 'err3'],
                        ],
                        'k25': 'error',
                    }
                },
                {
                    'k1': 'str', 'k2': {
                        'k21': 0,
                        'k22': [0],
                        'k23': [{'k231': 0}],
                        'k24': [[0]],
                        'k25': [[0]],
                    }
                },
                check_type=True,
            )
        )

        self.assertIn('k2.k22.2', errors)
        self.assertIn('k2.k23.1.k232', errors)
        self.assertIn('k2.k23.2.k231', errors)
        self.assertIn('k2.k24.1.0', errors)
        self.assertIn('k2.k25', errors)

    def test_check_root_type_error(self):
        errors = dict(check_json_schema(
            1, {'test': 'foo'}, check_type=False
        ))

        self.assertIn('', errors)

