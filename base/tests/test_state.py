# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from simple_history.models import HistoricalRecords
from base.test_utils.testcases import WLTempModelTestCase
from ..models.state import AbstractStateModel


test_app_label = 'test'


class DummyModel(models.Model):
    dummy_field = models.CharField(max_length=10)

    class Meta:
        app_label = test_app_label


def get_state_class():

    # Rename history model's app_label to 'test', which can avoid manage process raise ProgrammingError.
    def new_create_func(self, model, inherited):
        self.app = test_app_label
        return old_create_func(self, model, inherited)

    old_create_func = HistoricalRecords.create_history_model
    HistoricalRecords.create_history_model = new_create_func

    class State(AbstractStateModel):
        class Meta:
            app_label = test_app_label
            related_model = DummyModel
            foreign_key_kwargs = {'related_name': 'state'}
            foreign_field_name = 'rel'
            state_choices = (
                (0, 'state0'),
                (1, 'state1'),
            )

    HistoricalRecords.create_history_model = old_create_func

    return State


class TestStateModel(WLTempModelTestCase):

    State = get_state_class()

    temp_models = [
        DummyModel,
        State,
        'test.HistoricalState',
    ]

    def test_model(self):
        dm = DummyModel.objects.create(dummy_field='dummy')
        self.State.objects.create(
            state=0,
            rel=dm
        )

        dm.refresh_from_db()

        self.assertEqual(dm.state.state, 0)
