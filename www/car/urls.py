# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = patterns('www.car.views',

                       url(r'^get_serial_by_brand$', 'get_serial_by_brand'),
                       url(r'^get_car_basic_info_by_serial$', 'get_car_basic_info_by_serial'),
                       url(r'^evaluate_price$', 'evaluate_price'),
                       url(r'^sell_car$', 'sell_car'),
                       url(r'^get_top_5_evaluate_car$', 'get_top_5_evaluate_car'),
                       )
