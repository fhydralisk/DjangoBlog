# coding=utf-8
from __future__ import unicode_literals


from django.conf.urls import url

from .api import views


urlpatterns = [
    url(r'^stock/list/$', views.StockListView.as_view(), name='stock_list'),
    url(r'^journal/list/$', views.JournalListView.as_view(), name='journal_list'),
]
