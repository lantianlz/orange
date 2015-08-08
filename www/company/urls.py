# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('www.company.views',
	url(r'^booking$', 'booking'),
	url(r'^get_booking$', 'get_booking'),
)