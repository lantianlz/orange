# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.car_wash.models import Order, group_choices
from www.car_wash.interface import CarWashManagerBase
from www.account.interface import UserBase

@verify_permission('')
def manager(request, template_name='pc/admin/car_wash_manager.html'):
    order_state_choices = [{'value': x[0], 'name': x[1]} for x in Order.order_state_choices]
    pay_type_choices = [{'value': x[0], 'name': x[1]} for x in Order.pay_type_choices]
    # platform_choices = [{'value': x[0], 'name': x[1]} for x in Coupon.platform_choices]
    # state_choices = [{'value': x[0], 'name': x[1]} for x in Coupon.state_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_manager(objs, num):
    data = []

    for x in objs:
        num += 1

        user = UserBase().get_user_by_id(x.user_id) if x.user_id else None

        data.append({
            'num': num,
            'manager_id': x.id,
            'user_id': x.user_id if user else '',
            'user_nick': user.nick if user else '',
            'car_wash_id': x.car_wash.id if x.car_wash else '',
            'car_wash_name': x.car_wash.name if x.car_wash else '',
            'role': x.role
        })

    return data


@verify_permission('query_car_wash_manager')
def search(request):
    data = []

    car_wash_name = request.REQUEST.get('car_wash_name')
    
    page_index = int(request.REQUEST.get('page_index'))

    objs = CarWashManagerBase().search_managers_for_admin(car_wash_name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_manager(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_car_wash_manager')
def get_manager_by_id(request):
    manager_id = request.REQUEST.get('manager_id')

    data = format_manager([CarWashManagerBase().get_manager_by_id(manager_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_car_wash_manager')
@common_ajax_response
def modify_coupon(request):
    coupon_id = request.REQUEST.get('coupon_id')
    coupon_type = request.REQUEST.get('coupon_type')
    discount = request.REQUEST.get('discount')
    expiry_time = request.REQUEST.get('expiry_time')
    expiry_time = datetime.datetime.strptime(expiry_time, '%Y-%m-%d')
    user_id = request.REQUEST.get('user_id')
    minimum_amount = request.REQUEST.get('minimum_amount')
    car_wash_id = request.REQUEST.get('car_wash_id')

    return CouponBase().modify_coupon(
        coupon_id, coupon_type, discount, expiry_time, 
        user_id, minimum_amount, car_wash_id
    )


@verify_permission('add_car_wash_manager')
@common_ajax_response
def add_manager(request):
    car_wash_id = request.REQUEST.get('car_wash_id')
    manager = request.REQUEST.get('manager')

    flag, msg = CarWashManagerBase().add_car_wash_manager(
        car_wash_id, manager
    )

    return flag, msg.id if flag == 0 else msg


@verify_permission('delete_car_wash_manager')
@common_ajax_response
def delete_manager(request):
    manager_id = request.REQUEST.get('manager_id')

    return CarWashManagerBase().delete_car_wash_manager(manager_id)

