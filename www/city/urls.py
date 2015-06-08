# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = patterns('www.city.views',

                       url(r'^open_citys_list$', 'open_citys_list'),
                       url(r'^provinces_list$', 'provinces_list'),
                       url(r'^province/(?P<province_id>\d+)$', 'citys_list'),
                       url(r'^unopen_city/(?P<city_id>\d+)$', 'unopen_city'),
                       url(r'^select_city/(?P<city_id>\d+)$', 'select_city'),
                       )
