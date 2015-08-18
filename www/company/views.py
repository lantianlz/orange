# -*- coding: utf-8 -*-

import json
import time, datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import common_ajax_response, member_required, company_manager_required_for_request
from www.company.interface import BookingBase, CompanyManagerBase, MealBase, OrderBase, CashRecordBase, CashAccountBase
from www.account.interface import UserBase
from www.weixin.interface import WeixinBase, Sign
from www.company.models import Item


def booking(request, template_name='mobile/booking.html'):

    invite_by = request.REQUEST.get('invite_by')
    if invite_by:
        invite = UserBase().get_user_by_id(invite_by)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@common_ajax_response
def get_booking(request):

    company_name = request.REQUEST.get('company')
    staff_name = request.REQUEST.get('name')
    mobile = request.REQUEST.get('mobile')
    source = request.REQUEST.get('source')
    invite_by = request.REQUEST.get('invite_by')

    return BookingBase().add_booking(company_name, staff_name, mobile, source, invite_by)


@member_required
def invite(request, template_name='mobile/invite.html'):

    # 微信key
    url = 'http://www.3-10.cc/company/invite'
    sign = Sign(WeixinBase().get_weixin_jsapi_ticket(WeixinBase().init_app_key()), url)
    sign_dict = sign.sign()

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@member_required
def index(request):

    # 判断是否是公司管理员
    cm = CompanyManagerBase().get_cm_by_user_id(request.user.id)
    if cm:
        return HttpResponseRedirect("/company/%s/record" % cm.company.id)

    err_msg = u'权限不足，你还不是公司管理员，如有疑问请联系三点十分客服'
    return render_to_response('error.html', locals(), context_instance=RequestContext(request))

def format_order(objs, num):
    data = []

    for x in objs:
        num += 1

        create_operator = UserBase().get_user_by_id(x.create_operator)
        distribute_operator = UserBase().get_user_by_id(x.distribute_operator) if x.distribute_operator else ''
        confirm_operator = UserBase().get_user_by_id(x.confirm_operator) if x.confirm_operator else ''

        data.append({
            'num': num,
            'order_id': x.id,
            'order_no': x.order_no,
            'create_operator_id': create_operator.id,
            'create_operator_name': create_operator.nick,
            'create_time': x.create_time.strftime('%Y-%m-%d %H:%M'),
            'distribute_operator_id': distribute_operator.id if distribute_operator else '',
            'distribute_operator_name': distribute_operator.nick if distribute_operator else '',
            'distribute_time': x.distribute_time.strftime('%Y-%m-%d %H:%M') if x.distribute_time else '',
            'confirm_operator_id': confirm_operator.id if confirm_operator else '',
            'confirm_operator_name': confirm_operator.nick if confirm_operator else '',
            'confirm_time': x.confirm_time.strftime('%Y-%m-%d %H:%M') if x.confirm_time else '',
            'total_price': str(x.total_price),
            'note': x.note,
            'is_test': x.is_test,
            'state': x.state,
            'state_str': x.get_state_display()
        })

    return data

@member_required
@company_manager_required_for_request
def orders(request, company_id, template_name='pc/company/orders.html'):

    types = [{'value': x[0], 'name': x[1]} for x in Item.type_choices]

    now = datetime.datetime.now()
    start_date = request.REQUEST.get('start_date', now.replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.REQUEST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    order_no = request.REQUEST.get('order_no')
    
    objs = OrderBase().search_orders_by_company(company_id, start_date, end_date, order_no)

    page_index = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(objs, count=10, page=page_index).info
    page_params = (page_objs[1], page_objs[4])

    num = 10 * (page_index - 1)
    data = format_order(page_objs[0], num)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_item(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'code': x.item.code,
            'name': x.item.name,
            'amount': x.amount if x.item.integer == 2 else int(x.amount), # 非水果类 数量转为int
            'spec': x.item.get_spec_display(),
            'type': x.item.item_type,
            'type_str': x.item.get_item_type_display()
        })

    return data

@member_required
def get_order_detail(request):
    order_id = request.REQUEST.get('order_id')

    data = format_item(OrderBase().get_items_of_order(order_id), 0)

    return HttpResponse(json.dumps(data), mimetype='application/json')

@member_required
@company_manager_required_for_request
def meal(request, company_id, template_name='pc/company/meal.html'):
    meal = MealBase().get_meal_by_company(company_id)
    if meal:
        items = MealBase().get_items_of_meal(meal.id)

        data = {}
        for item in items:

            key = item.item.item_type
            if not data.has_key(key):
                data[key] = []

            data[key].append({
                'code': item.item.code,
                'name': item.item.name,
                'amount': item.amount if item.item.integer == 2 else int(item.amount), # 非水果类 数量转为int
                'spec': item.item.get_spec_display(),
                'type': item.item.get_item_type_display()
            })

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@member_required
@company_manager_required_for_request
def deposit(request, company_id, template_name='pc/company/deposit.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_record(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'record_id': x.id,
            'value': str(x.value),
            'current_balance': str(x.current_balance),
            'operation': x.operation,
            'notes': x.notes,
            'create_time': x.create_time.strftime('%Y-%m-%d %H:%M')
        })

    return data

@member_required
@company_manager_required_for_request
def record(request, company_id, template_name='pc/company/record.html'):
    now = datetime.datetime.now()
    start_date = request.REQUEST.get('start_date', now.replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.REQUEST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)

    account = CashAccountBase().get_account_by_company(company_id)
    objs = CashRecordBase().get_records_by_company(company_id, start_date, end_date)

    page_index = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(objs, count=10, page=page_index).info
    page_params = (page_objs[1], page_objs[4])

    num = 10 * (page_index - 1)
    data = format_record(page_objs[0], num)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@member_required
@company_manager_required_for_request
def feedback(request, company_id, template_name='pc/company/feedback.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))