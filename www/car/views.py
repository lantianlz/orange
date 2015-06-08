# -*- coding: utf-8 -*-

import urllib
import json
import datetime
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

import common.utils
from www.misc.decorators import common_ajax_response
from car.interface import BrandBase, SerialBase, CarBasicInfoBase, UserUsedCarBase


def car(request, template_name='pc/index.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def get_serial_by_brand(request):
    data = []

    brand_id = request.REQUEST.get('brand_id')

    for x in SerialBase().get_serial_by_brand(brand_id, True):
        data.append({
            'value': x.id,
            'name': x.name,
            'group': x.brand.name
        })

    return HttpResponse(json.dumps(data))


def get_car_basic_info_by_serial(request):
    data = []

    serial_id = request.REQUEST.get('serial_id')

    for x in CarBasicInfoBase().get_car_basic_info_by_serial(serial_id, True):
        data.append({
            'value': x.id,
            'name': x.name,
            'group': x.year
        })

    return HttpResponse(json.dumps(data))


def evaluate_price(request):
    car_basic_info_id = request.REQUEST.get('car_basic_info_id')
    year = request.REQUEST.get('year')
    month = request.REQUEST.get('month')
    get_license_time = datetime.datetime(year=int(year), month=int(month), day=1)
    trip_distance = request.REQUEST.get('distance')
    ip = common.utils.get_clientip(request)

    flag, obj, price = UserUsedCarBase().evaluate_price(car_basic_info_id, get_license_time, trip_distance, ip)

    data = {}
    if flag == 0:
        data = {
            'user_used_car_id': obj.id,
            'name': obj.car.name,
            'serial_name': obj.car.serial.name,
            'price': str(price),
            'original_price': str(obj.car.original_price),
            'license_time': obj.get_license_time.strftime('%Y年 %m月'),
            'trip_distance': obj.trip_distance,
            'img': obj.car.img
        }

    return HttpResponse(json.dumps({'errcode': flag, 'data': data}))


@common_ajax_response
def sell_car(request):
    user_used_car_id = request.REQUEST.get('user_used_car_id')
    mobile = request.REQUEST.get('mobile')

    return UserUsedCarBase().sell_car(user_used_car_id, mobile)


def get_top_5_evaluate_car(request):
    data = []

    for x in UserUsedCarBase().get_top_5_evaluate_car():

        serial = SerialBase().get_serial_by_id(x['car__serial__id'])[0]
        data.append({
            'name': serial.name,
            'count': x['total']
        })

    return HttpResponse(json.dumps(data))
