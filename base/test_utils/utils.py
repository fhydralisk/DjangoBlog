from django.urls import resolve, reverse
from django.http import Http404

from base.util.db import update_instance_from_dict
from base.views import WLAPIGenericView
from base.choices.common import serializer_type_choice


class ReconstructModelMixin(object):
    @staticmethod
    def update_instances(objs, field_values):
        if hasattr(field_values, 'next'):
            # Check if field_values is an iterator.
            field_values = field_values.next()

        for obj in objs:
            update_instance_from_dict(obj, field_values, True)

    def reconstruct_data_with_queryset(self, include, exclude, field_values_include, field_values_exclude):
        self.update_instances(include, field_values_include)
        self.update_instances(exclude, field_values_exclude)

    def reconstruct_data_with_count(self, model, count, field_values_include, field_values_exclude):
        include = model.objects.all()[:count]
        exclude = model.objects.all()[count:]
        self.reconstruct_data_with_queryset(include, exclude, field_values_include, field_values_exclude)


class ResolveViewSerializerMixin(object):

    view_name = None
    path = None
    method = 'get'

    @property
    def api_serializer(self):
        return self.get_serializer(serializer_type_choice.ST_API)

    @property
    def result_serializer(self):
        return self.get_serializer(serializer_type_choice.ST_RESULT)

    def get_serializer(self, serializer_type):
        if self.path is not None:
            func, args, kwargs = resolve(self.path)
        elif self.view_name is not None:
            func, args, kwargs = resolve(reverse(self.view_name))
        else:
            raise Http404()

        if hasattr(func, 'cls'):
            if issubclass(func.cls, WLAPIGenericView):
                return func.cls.determine_serializer_by_request_method(self.method, serializer_type)

        raise TypeError('Class of view %s is not subclass of WLAPIGenericView' % getattr(func, 'cls', None))
