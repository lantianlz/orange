# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.car_wash.models import group_choices
from www.car_wash.interface import ServicePriceBase, ServiceTypeBase

@verify_permission('')
def service_price(request, template_name='pc/admin/service_price.html'):
    service_types = [{'value': x.id, 'name': x.name} for x in ServiceTypeBase().get_all_types(True)]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_price(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'price_id': x.id,
            'car_wash_id': x.car_wash.id,
            'car_wash_name': x.car_wash.name,
            'service_type_id': x.service_type.id,
            'service_type_name': x.service_type.name,
            'sale_price': x.sale_price,
            'origin_price': x.origin_price,
            'clear_price': x.clear_price,
            'sort_num': x.sort_num,
            'state': x.state
        })

    return data


@verify_permission('query_service_price')
def search(request):
    data = []

    car_wash_name = request.REQUEST.get('car_wash_name')
    state = request.REQUEST.get('state')
    state = True if state == "1" else False 
    page_index = int(request.REQUEST.get('page_index'))

    objs = ServicePriceBase().search_prices_for_admin(car_wash_name, state)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_price(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_service_price')
def get_service_price_by_id(request):
    price_id = request.REQUEST.get('price_id')

    data = format_price([ServicePriceBase().get_service_price_by_id(price_id, None)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_service_price')
@common_ajax_response
def modify_service_price(request):
    price_id = request.REQUEST.get('price_id')
    car_wash_id = request.REQUEST.get('car_wash_id')
    service_type_id = request.REQUEST.get('service_type_id')
    sale_price = request.REQUEST.get('sale_price')
    origin_price = request.REQUEST.get('origin_price')
    clear_price = request.REQUEST.get('clear_price')
    sort_num = int(request.REQUEST.get('sort'))
    state = request.REQUEST.get('state')
    state = True if state == "1" else False

    return ServicePriceBase().modify_service_price(
        price_id, car_wash_id, service_type_id, sale_price, 
        origin_price, clear_price, sort_num, state
    )


@verify_permission('add_service_price')
@common_ajax_response
def add_service_price(request):
    car_wash_id = request.REQUEST.get('car_wash_id')
    service_type_id = request.REQUEST.get('service_type_id')
    sale_price = request.REQUEST.get('sale_price')
    origin_price = request.REQUEST.get('origin_price')
    clear_price = request.REQUEST.get('clear_price')
    sort_num = int(request.REQUEST.get('sort'))

    flag, msg = ServicePriceBase().add_service_price(
        car_wash_id, service_type_id, sale_price, 
        origin_price, clear_price, sort_num
    )

    return flag, msg.id if flag == 0 else msg


@verify_permission('remove_service_price')
@common_ajax_response
def remove_service_price(request):
    price_id = request.REQUEST.get('price_id')

    return ServicePriceBase().remove_service_price(price_id)