# -*- coding: utf-8 -*-

import json
import urllib
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required

from www.car_wash.interface import CarWashBase
from www.city.interface import CityBase

@verify_permission('')
def car_wash(request, template_name='pc/admin/car_wash.html'):
    from www.car_wash.models import CarWash
    wash_type_choices = [{'name': x[1], 'value': x[0]} for x in CarWash.wash_type_choices]

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_car_wash(objs, num):
    data = []

    for x in objs:
        num += 1

        city = CityBase().get_city_by_id(x.city_id)

        data.append({
            'num': num,
            'car_wash_id': x.id,
            'name': x.name,
            'business_hours': x.business_hours,
            'city_id': x.city_id,
            'city_name': city.city if city else '',
            'district_id': x.district_id,
            'district_name': '',
            'tel': x.tel,
            'addr': x.addr,
            'longitude': x.longitude,
            'latitude': x.latitude,
            'wash_type': x.wash_type,
            'des': x.des,
            'note': x.note,
            'lowest_sale_price': x.lowest_sale_price,
            'lowest_origin_price': x.lowest_origin_price,
            'imgs': x.imgs,
            'cover': x.cover,
            'rating': x.rating,
            'order_count': x.order_count,
            'valid_date_start': str(x.valid_date_start),
            'valid_date_end': str(x.valid_date_end),
            'is_vip': x.is_vip,
            'vip_info': x.vip_info,
            'sort_num': x.sort_num,
            'state': x.state,
            'company_id': x.company.id if x.company else '',
            'company_name': x.company.name if x.company else '',
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_car_wash')
def search(request):
    name = request.REQUEST.get('name')
    state = request.REQUEST.get('state')
    state = True if state == "1" else False
    page_index = int(request.REQUEST.get('page_index', 1))

    objs = CarWashBase().search_car_washs_for_admin(name, state)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_car_wash(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )

@verify_permission('add_car_wash')
@common_ajax_response
def add_car_wash(request):
    city_id = request.REQUEST.get('city_id')
    company_id = request.REQUEST.get("company_id")
    district_id = request.REQUEST.get('district_id')
    name = request.REQUEST.get('name')
    business_hours = request.REQUEST.get('business_hours')
    tel = request.REQUEST.get('tel')
    addr = request.REQUEST.get('addr')
    lowest_sale_price = request.REQUEST.get('lowest_sale_price')
    lowest_origin_price = request.REQUEST.get('lowest_origin_price')
    longitude = request.REQUEST.get('longitude')
    latitude = request.REQUEST.get('latitude')
    imgs = request.REQUEST.get('imgs')
    cover = request.REQUEST.get('cover')
    wash_type = request.REQUEST.get('wash_type')
    des = request.REQUEST.get('des')
    note = request.REQUEST.get('note')
    sort_num = request.REQUEST.get('sort_num')
    state = request.REQUEST.get('state')
    state = True if state == "1" else False

    flag, msg = CarWashBase().add_car_wash(city_id, district_id, name, business_hours, tel, 
        addr, lowest_sale_price, lowest_origin_price, longitude, latitude, imgs, cover,
        wash_type, des, note, sort_num, state, company_id)

    return flag, msg.id if flag == 0 else msg


@verify_permission('query_car_wash')
def get_car_wash_by_id(request):
    car_wash_id = request.REQUEST.get('car_wash_id')

    obj = CarWashBase().get_car_wash_by_id(car_wash_id, None)

    data = ""

    if obj:
        data = format_car_wash([obj], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_car_wash')
@common_ajax_response
def modify_car_wash(request):

    car_wash_id = request.REQUEST.get("car_wash_id")
    company_id = request.REQUEST.get("company_id")
    city_id = request.REQUEST.get('city_id')
    district_id = request.REQUEST.get('district_id')
    name = request.REQUEST.get('name')
    business_hours = request.REQUEST.get('business_hours')
    tel = request.REQUEST.get('tel')
    addr = request.REQUEST.get('addr')
    lowest_sale_price = request.REQUEST.get('lowest_sale_price')
    lowest_origin_price = request.REQUEST.get('lowest_origin_price')
    longitude = request.REQUEST.get('longitude')
    latitude = request.REQUEST.get('latitude')
    imgs = request.REQUEST.get('imgs')
    cover = request.REQUEST.get('cover')
    wash_type = request.REQUEST.get('wash_type')
    des = request.REQUEST.get('des')
    note = request.REQUEST.get('note')
    sort_num = request.REQUEST.get('sort_num')
    state = request.REQUEST.get('state')
    state = True if state == "1" else False

    return CarWashBase().modify_car_wash(car_wash_id, city_id, district_id, name, business_hours, tel, 
        addr, lowest_sale_price, lowest_origin_price, longitude, latitude, imgs, cover,
        wash_type, des, note, sort_num, state, company_id)

@member_required
def get_car_washs_by_name(request):
    '''
    根据名字查询洗车行
    '''
    car_wash_name = request.REQUEST.get('car_wash_name')
    state = request.REQUEST.get('state')
    state = None if state == "0" else True

    result = []

    car_washs = CarWashBase().get_car_washs_by_name(car_wash_name, state)

    if car_washs:
        for x in car_washs:
            result.append([x.id, x.name, None, x.name])

    return HttpResponse(json.dumps(result), mimetype='application/json')