# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from base.models import AliSmsAPIMasterKey

# Register your models here.

admin.site.register([AliSmsAPIMasterKey, ])


class ReadOnlyAdminMixin(object):
    """Disables all editing capabilities."""
    change_form_template = "admin/view.html"

    def __init__(self, *args, **kwargs):
        super(ReadOnlyAdminMixin, self).__init__(*args, **kwargs)
        self.readonly_fields = self.model._meta.get_all_field_names()

    def get_actions(self, request):
        actions = super(ReadOnlyAdminMixin, self).get_actions(request)
        del_action = "delete_selected"
        if del_action in actions:
            del actions[del_action]
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass

    def delete_model(self, request, obj):
        pass

    def save_related(self, request, form, formsets, change):
        pass
