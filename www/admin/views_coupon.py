# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.car_wash.models import Coupon, group_choices
from www.car_wash.interface import CouponBase
from www.account.interface import UserBase

@verify_permission('')
def coupon(request, template_name='pc/admin/coupon.html'):
    coupon_group_choices = [{'value': x[0], 'name': x[1]} for x in group_choices]
    coupon_type_choices = [{'value': x[0], 'name': x[1]} for x in Coupon.coupon_type_choices]
    platform_choices = [{'value': x[0], 'name': x[1]} for x in Coupon.platform_choices]
    state_choices = [{'value': x[0], 'name': x[1]} for x in Coupon.state_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_coupon(objs, num):
    data = []

    for x in objs:
        num += 1

        user = UserBase().get_user_by_id(x.user_id) if x.user_id else None

        data.append({
            'num': num,
            'coupon_id': x.id,
            'code': x.code,
            'coupon_type': x.coupon_type,
            'discount': x.discount,
            'expiry_time': str(x.expiry_time)[:10],
            'minimum_amount': x.minimum_amount,
            'user_id': x.user_id if user else '',
            'user_nick': user.nick if user else '',
            'car_wash_id': x.car_wash.id if x.car_wash else '',
            'car_wash_name': x.car_wash.name if x.car_wash else '',
            'state': x.state
        })

    return data


@verify_permission('query_coupon')
def search(request):
    data = []

    car_wash_name = request.REQUEST.get('car_wash_name')
    nick = request.REQUEST.get('nick')
    state = request.REQUEST.get('state')
    state = int(state) if state != "-1" else None
    
    page_index = int(request.REQUEST.get('page_index'))

    objs = CouponBase().search_coupons_for_admin(car_wash_name, nick, state)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_coupon(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_coupon')
def get_coupon_by_id(request):
    coupon_id = request.REQUEST.get('coupon_id')

    data = format_coupon([CouponBase().get_coupon_by_id(coupon_id, None, None)], 1)[0]

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
    state = request.REQUEST.get('state')

    return CouponBase().modify_coupon(
        coupon_id, coupon_type, discount, expiry_time, 
        user_id, minimum_amount, car_wash_id, state
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