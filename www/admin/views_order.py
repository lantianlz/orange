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
from www.car_wash.interface import OrderBase
from www.account.interface import UserBase

@verify_permission('')
def order(request, template_name='pc/admin/order.html'):
    order_state_choices = [{'value': x[0], 'name': x[1]} for x in Order.order_state_choices]
    pay_type_choices = [{'value': x[0], 'name': x[1]} for x in Order.pay_type_choices]
    # platform_choices = [{'value': x[0], 'name': x[1]} for x in Coupon.platform_choices]
    # state_choices = [{'value': x[0], 'name': x[1]} for x in Coupon.state_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_order(objs, num):
    data = []

    for x in objs:
        num += 1

        user = UserBase().get_user_by_id(x.user_id) if x.user_id else None

        data.append({
            'num': num,
            'order_id': x.id,
            'trade_id': x.trade_id,
            'service_type': x.service_price.service_type.name,
            'source_type': x.source_type,
            'user_id': x.user_id if user else '',
            'user_nick': user.nick if user else '',
            'car_wash_id': x.car_wash.id if x.car_wash else '',
            'car_wash_name': x.car_wash.name if x.car_wash else '',
            'sale_price': str(x.service_price.sale_price),
            'origin_price': str(x.service_price.origin_price),
            'clear_price': str(x.service_price.clear_price),
            'count': x.count,
            'coupon_code': x.coupon.code if x.coupon else '',
            'coupon_type': x.coupon.coupon_type if x.coupon else '',
            'coupon_discount': x.coupon.discount  if x.coupon else '',
            'total_fee': str(x.total_fee),
            'discount_fee': str(x.discount_fee),
            'user_cash_fee': str(x.user_cash_fee),
            'pay_fee': str(x.pay_fee),
            'pay_type': str(x.pay_type),
            'pay_time': str(x.pay_time),
            'pay_info': x.pay_info,
            'ip': x.ip,
            'state': x.order_state
        })

    return data


@verify_permission('query_order')
def search(request):
    data = []

    car_wash_name = request.REQUEST.get('car_wash_name')
    trade_id = request.REQUEST.get('trade_id')
    nick = request.REQUEST.get('nick')
    state = request.REQUEST.get('state')
    state = int(state) if state != "-2" else None
    
    page_index = int(request.REQUEST.get('page_index'))

    objs = OrderBase().search_orders_for_admin(car_wash_name, trade_id, nick, state)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_order(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_order')
def get_order_by_id(request):
    order_id = request.REQUEST.get('order_id')

    data = format_order([OrderBase().get_order_by_id(order_id, None)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_coupon')
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


@verify_permission('add_coupon')
@common_ajax_response
def add_coupon(request):
    coupon_type = request.REQUEST.get('coupon_type')
    discount = request.REQUEST.get('discount')
    expiry_time = request.REQUEST.get('expiry_time')
    expiry_time = datetime.datetime.strptime(expiry_time, '%Y-%m-%d')
    user_id = request.REQUEST.get('user_id')
    minimum_amount = request.REQUEST.get('minimum_amount')
    car_wash_id = request.REQUEST.get('car_wash_id')

    flag, msg = CouponBase().add_coupon(
        coupon_type, discount, expiry_time, 
        user_id, minimum_amount, car_wash_id
    )

    return flag, msg.id if flag == 0 else msg