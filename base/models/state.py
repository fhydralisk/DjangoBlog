# coding=utf-8
from __future__ import unicode_literals

import six

from django.db import models
from django.db.models.base import ModelBase
from django_fsm import FSMIntegerField
from simple_history.models import HistoricalRecords


class AbstractStateModelMeta(ModelBase):
    def __new__(mcs, name, bases, attrs):
        parents = [b for b in bases if isinstance(b, AbstractStateModelMeta)]
        if not parents:
            return super(ModelBase, mcs).__new__(mcs, name, bases, attrs)

        meta = attrs.get('Meta', None)
        if meta is None:
            raise AssertionError("Missing Meta in StateModel %s" % name)
        else:
            related_model = meta.__dict__.pop('related_model', None)
            foreign_key_kwargs = meta.__dict__.pop('foreign_key_kwargs', None) or {}
            foreign_field_name = meta.__dict__.pop('foreign_field_name', 'rel')
            state_choices = meta.__dict__.pop('state_choices', None)
            if getattr(meta, 'abstract', False):
                pass
            else:
                if related_model is not None:
                    attrs[foreign_field_name] = models.OneToOneField(
                        to=related_model,
                        **foreign_key_kwargs
                    )
                    if state_choices:
                        first_element = state_choices[0]
                        if len(first_element) == 2:
                            attrs['state'] = FSMIntegerField(db_index=True, choices=state_choices)
                        elif len(first_element) == 3:
                            attrs['state'] = FSMIntegerField(db_index=True, state_choices=state_choices)
                        else:
                            raise AssertionError("state_choice must be a list of Tuple2 or Tuple3")
                    else:
                        raise AssertionError('Missing "state_choice" field in Meta')

        return super(AbstractStateModelMeta, mcs).__new__(mcs, name, bases, attrs)


# noinspection PyTypeChecker
ModelWithStateMeta = AbstractStateModelMeta(
    b'ModelWithStateMeta', (models.Model, ) + models.Model.__bases__, dict(models.Model.__dict__)
)


class AbstractStateModel(ModelWithStateMeta):
    state = FSMIntegerField(db_index=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True
        related_model = None
        foreign_key_kwargs = None
        foreign_field_name = 'rel'
        state_choices = None
