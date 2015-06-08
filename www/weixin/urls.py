# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('www.weixin.views',
                       url(r'^/?$', 'index'),
                       )
