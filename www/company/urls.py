# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('www.company.views',

                       url(r'^$', 'index'),
                       url(r'^(?P<company_id>\d+)/orders$', 'orders'),
                       url(r'^(?P<company_id>\d+)/meal$', 'meal'),
                       url(r'^(?P<company_id>\d+)/deposit$', 'deposit'),
                       url(r'^(?P<company_id>\d+)/record$', 'record'),
                       url(r'^(?P<company_id>\d+)/feedback$', 'feedback'),
                       url(r'^(?P<company_id>\d+)/product_list$', 'product_list'),
                       url(r'^(?P<company_id>\d+)/list_orders$', 'list_orders'),
                       url(r'^(?P<company_id>\d+)/print_order/(?P<order_no>\w+)$', 'print_order'),

                       url(r'^booking$', 'booking'),
                       url(r'^invite$', 'invite'),
                       url(r'^get_booking$', 'get_booking'),
                       url(r'^introduction_m$', 'introduction_m'),
                       url(r'^success$', 'success'),
                       url(r'^error$', 'error'),

                       url(r'^concat_order_item$', 'concat_order_item'),
                       )
