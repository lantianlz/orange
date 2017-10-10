# -*- coding: utf-8 -*-

import json
import time
import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import common_ajax_response, member_required, company_manager_required_for_request, request_limit_by_ip
from www.company.interface import BookingBase, CompanyManagerBase, MealBase, OrderBase, CashRecordBase, CashAccountBase, ItemBase, RechargeOrderBase
from www.account.interface import UserBase
from www.weixin.interface import WeixinBase, Sign
from www.company.models import Item


def booking(request, template_name='mobile/booking.html'):
    '''
    手机版预定
    '''
    url = u'http://%s' % (request.get_host() + request.get_full_path())
    sign = Sign(WeixinBase().get_weixin_jsapi_ticket(WeixinBase().init_app_key()), url)
    sign_dict = sign.sign()

    invite_by = request.REQUEST.get('invite_by')
    if invite_by:
        invite = UserBase().get_user_by_id(invite_by)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@common_ajax_response
@request_limit_by_ip(10, 600)
def get_booking(request):
    '''
    提交预定试吃
    '''
    company_name = request.REQUEST.get('company')
    staff_name = request.REQUEST.get('name')
    mobile = request.REQUEST.get('mobile')
    source = request.REQUEST.get('source')
    invite_by = request.REQUEST.get('invite_by')

    return BookingBase().add_booking(company_name, staff_name, mobile, source, invite_by)


@member_required
def invite(request, template_name='mobile/invite.html'):
    '''
    手机版邀请
    '''
    # 微信key
    url = u'http://%s' % (request.get_host() + request.get_full_path())
    sign = Sign(WeixinBase().get_weixin_jsapi_ticket(WeixinBase().init_app_key()), url)
    sign_dict = sign.sign()

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def index(request):
    '''
    公司管理首页
    '''
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
            'person_count': x.person_count,
            'note': x.note,
            'is_test': x.is_test,
            'state': x.state,
            'state_str': x.get_state_display()
        })

    return data


@member_required
@company_manager_required_for_request
def orders(request, company_id, template_name='pc/company/orders.html'):
    '''
    订单列表
    '''
    # types = [{'value': x[0], 'name': x[1]} for x in Item.type_choices]

    now = datetime.datetime.now()
    start_date = request.REQUEST.get('start_date', now.replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.REQUEST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    order_no = request.REQUEST.get('order_no')

    objs, total_price = OrderBase().search_orders_by_company(company_id, start_date, end_date, order_no)

    page_index = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(objs, count=10, page=page_index).info
    page_params = (page_objs[1], page_objs[4])

    num = 10 * (page_index - 1)
    data = format_order(page_objs[0], num)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
@company_manager_required_for_request
def meal(request, company_id, template_name='pc/company/meal.html'):
    '''
    套餐
    '''
    meal = MealBase().get_meal_by_company(company_id)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
@company_manager_required_for_request
def deposit(request, company_id, template_name='pc/company/deposit.html'):
    '''
    在线充值
    '''
    account = CashAccountBase().get_account_by_company(company_id)

    total_fee = abs(account.balance)

    if request.method == "POST":
        from common.alipay import alipay_pc
        total_fee = request.POST.get('total_fee')
        pay_type = request.POST.get('pay_type')

        flag, msg = RechargeOrderBase().create_order(company_id, total_fee, pay_type, utils.get_clientip(request))

        if flag == 0:
            order = msg

            return HttpResponseRedirect(
                alipay_pc.create_direct_pay_by_user(
                    order.trade_id,
                    u"三点十分下午茶",
                    u"水果，点心，热饮",
                    total_fee
                )
            )
        warning_msg = msg

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
    '''
    充值记录
    '''
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
    '''
    反馈
    '''
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def introduction_m(request, template_name='mobile/introduction_m.html'):
    '''
    手机版产品介绍
    '''
    # 微信key
    url = u'http://%s' % (request.get_host() + request.get_full_path())
    sign = Sign(WeixinBase().get_weixin_jsapi_ticket(WeixinBase().init_app_key()), url)
    sign_dict = sign.sign()

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
@company_manager_required_for_request
def product_list(request, company_id, template_name='pc/company/product_list.html'):
    '''
    产品目录
    '''
    fruit = ItemBase().get_items_by_type(1, [1])
    cake = ItemBase().get_items_by_type(2, [1])
    supplies = ItemBase().get_items_by_type(90, [1])
    recycle = ItemBase().get_items_by_type(91, [1])
    drink = ItemBase().get_items_by_type(3, [1])
    luwei = ItemBase().get_items_by_type(4, [1])

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def customers(request):
    '''
    官网典型客户
    '''
    from www.company.interface import CompanyBase, OrderBase
    companys = CompanyBase().get_companys_by_show()
    serviced_company_count = CompanyBase().get_serviced_company_count()
    person_time_count = OrderBase().get_active_person_time_count()
    return render_to_response('static_templates/customers.html', locals(), context_instance=RequestContext(request))


def anonymous_product_list(request):
    '''
    匿名产品目录
    '''

    fruit = ItemBase().get_items_by_type(1, [1])
    cake = ItemBase().get_items_by_type(2, [1])
    # supplies = ItemBase().get_items_by_type(90, [1])
    # recycle = ItemBase().get_items_by_type(91, [1])
    drink = ItemBase().get_items_by_type(3, [1])
    luwei = ItemBase().get_items_by_type(4, [1])

    return render_to_response('static_templates/product_list.html', locals(), context_instance=RequestContext(request))


@member_required
def success(request, template_name='pc/company/success.html'):
    '''
    成功页面
    '''

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def error(request, template_name='pc/company/error.html'):
    '''
    失败页面
    '''

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@company_manager_required_for_request
def list_orders(request, company_id, template_name='pc/company/list_orders.html'):
    '''
    订单汇总
    '''

    now = datetime.datetime.now()
    start_date = request.REQUEST.get('start_date', now.replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.REQUEST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    order_no = request.REQUEST.get('order_no')

    objs, total_price = OrderBase().search_orders_by_company(company_id, start_date, end_date, order_no, True)

    page_index = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(objs, count=1000, page=page_index).info
    page_params = (page_objs[1], page_objs[4])

    num = 1000 * (page_index - 1)
    data = format_order(page_objs[0], num)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def concat_order_item(request):
    '''
    将订单下项目名称拼装成一个字符串
    '''
    from company.models import OrderItem

    order_no = request.REQUEST.get('order_no')

    items = []
    for x in OrderItem.objects.filter(order__order_no=order_no):
        items.append(x.item.name)
    names = u'，'.join(items) if items else order_no
    return HttpResponse(json.dumps({'names': names}), mimetype='application/json')


def anonymous_fruit_price(request):
    '''
    匿名产品目录
    '''

    items = ItemBase().get_items_by_type(1, [1]).order_by('-update_time')
    today = datetime.datetime.now()

    return render_to_response('static_templates/fruit_price.html', locals(), context_instance=RequestContext(request))


@member_required
@company_manager_required_for_request
def print_order(request, company_id, order_no, template_name='pc/admin/print_order.html'):

    order = OrderBase().get_order_by_order_no(order_no)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
