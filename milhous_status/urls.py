# coding=utf-8
from __future__ import unicode_literals


from django.conf.urls import url

from .api import views


urlpatterns = [
    url(r'^host/state/$', views.MilhousHostStatisticsReportView.as_view(), name='host_state'),
    url(r'^host/state/list/$', views.MilhousHostStatisticsListView.as_view(), name='host_state_list'),
    url(r'^host/list/$', views.MilhousHostListView.as_view(), name='host_list'),
]
