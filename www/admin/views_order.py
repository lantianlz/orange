# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.company.models import Order, Item, Meal
from www.company.interface import OrderBase, MealBase, CompanyBase, SupplierBase
from www.account.interface import UserBase

@verify_permission('')
def order(request, template_name='pc/admin/order.html'):
    states = [{'value': x[0], 'name': x[1]} for x in Order.state_choices]
    all_states = [{'value': x[0], 'name': x[1]} for x in Order.state_choices]
    all_states.append({'value': -2, 'name': u"全部有效订单"})
    types = [{'name': x[1], 'value': x[0]} for x in Meal.type_choices]

    today = datetime.datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    start_date = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('')
def create_order(request, template_name='pc/admin/create_order.html'):
    types = [{'name': x[1], 'value': x[0]} for x in Meal.type_choices]

    today = datetime.datetime.now()
    weekday = today.date().weekday() + 2
    weekday = 1 if weekday == 8 else weekday
    start_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_order(objs, num, show_items=False):
    data = []

    for x in objs:
        num += 1

        meal = MealBase().get_meal_by_id(x.meal_id)
        company = CompanyBase().get_company_by_id(x.company_id)
        owner = UserBase().get_user_by_id(x.owner) if x.owner else None
        create_operator = UserBase().get_user_by_id(x.create_operator)
        distribute_operator = UserBase().get_user_by_id(x.distribute_operator) if x.distribute_operator else ''
        confirm_operator = UserBase().get_user_by_id(x.confirm_operator) if x.confirm_operator else ''

        items = []
        # 显示子项
        if show_items:
            for i in OrderBase().get_items_of_order(x.id):
                items.append({
                    'item_id': i.item.id,
                    'name': i.item.name,
                    'price': str(i.price),
                    'net_weight_price': str(i.price),
                    'sale_price': str(i.sale_price),
                    'item_type': i.item.item_type,
                    'spec': i.item.spec,
                    'spec_text': i.item.get_spec_display(),
                    'code': i.item.code,
                    'img': i.item.img,
                    'des': i.item.des,
                    'smart_des': i.item.smart_des(),
                    'amount': i.amount
                })

        data.append({
            'num': num,
            'order_id': x.id,
            'meal_id': meal.id,
            'meal_name': u'%s [¥%s]' % (meal.name, meal.price),
            'company_id': company.id,
            'company_name': company.name,
            'company_combine_name': company.combine_name(),
            'company_addr': company.addr,
            'company_logo': company.get_logo(),
            'company_tel': company.tel,
            'longitude': company.longitude,
            'latitude': company.latitude,
            'order_no': x.order_no,
            'create_operator_id': create_operator.id,
            'create_operator_name': create_operator.nick,
            'create_time': str(x.create_time),
            'distribute_operator_id': distribute_operator.id if distribute_operator else '',
            'distribute_operator_name': distribute_operator.nick if distribute_operator else '',
            'distribute_time': str(x.distribute_time) if x.distribute_time else '',
            'confirm_operator_id': confirm_operator.id if confirm_operator else '',
            'confirm_operator_name': confirm_operator.nick if confirm_operator else '',
            'confirm_time': str(x.confirm_time) if x.confirm_time else '',
            'total_price': str(x.total_price),
            'cost_price': str(x.cost_price),
            'person_count': x.person_count,
            'note': x.note,
            'rate': x.rate(),
            'is_test': x.is_test,
            'items': items,
            'owner_id': owner.id if owner else '',
            'owner_nick': owner.nick if owner else '',
            'expected_time': str(x.expected_time)[11:16],
            'state': x.state
        })
    
    return data

def _need_notice(obj):
    '''
    是否需要提示
    '''
    flag = False
    today = datetime.datetime.now()
    weekday = today.date().weekday() + 2
    weekday = 1 if weekday == 8 else weekday

    # 每周
    if obj.t_type == 1:
        flag = ((obj.cycle or '0-0-0-0-0-0-0').find(str(weekday)) > -1)

    # 隔周
    if obj.t_type == 2:
        temp = OrderBase().get_latest_order_of_company(obj.company.id)
        if not temp:
            flag = ((obj.cycle or '0-0-0-0-0-0-0').find(str(weekday)) > -1)
        else:
            flag = (((today - temp.confirm_time).days > 7) and ((obj.cycle or '0-0-0-0-0-0-0').find(str(weekday)) > -1))
    
    # 单次
    if obj.t_type == 3:
        flag = (obj.cycle == (today+datetime.timedelta(days=1)).strftime('%Y-%m-%d'))

    return int(flag)

def format_uncreate_order(objs, num):
    
    data = []

    for x in objs:
        num += 1

        company = CompanyBase().get_company_by_id(x.company_id)

        data.append({
            'num': num,
            'order_id': '',
            'meal_id': x.id,
            'meal_name': u'%s [¥%s]' % (x.name, x.price),
            'company_id': company.id,
            'company_name': u'%s[%s人]' % (company.name, company.person_count),
            'order_no': '',
            'create_time': '',
            'total_price': '',
            'is_test': '',
            'cycle': x.cycle or '0-0-0-0-0-0-0',
            't_type': x.t_type or '1',
            'need_notice': _need_notice(x),
            'cycle_str': x.get_cycle_str() if x.t_type != 3 else '',
            'state': -1
        })

    # 排序 需要提醒的排列在前面
    data.sort(key=lambda x:x['need_notice'], reverse=True)
    return data

@verify_permission('query_order')
def search(request):
    data = []

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)

    state = request.POST.get('state', '-1')
    state = int(state)
    company = request.POST.get('company')
    is_test = request.POST.get('is_test', '0')
    is_test = True if is_test == "1" else False
    owner = request.POST.get('owner')
    expected_time_sort = request.POST.get('expected_time_sort')
    expected_time_sort = True if expected_time_sort == "1" else False
    
    page_index = int(request.REQUEST.get('page_index'))
    sum_price = 0
    
    if state == -1:
        end_date = str(start_date)[:10]+' 23:59:59'
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        objs = OrderBase().search_uncreate_orders_for_admin(start_date, end_date)
    else:
        objs, sum_price = OrderBase().search_orders_for_admin(start_date, end_date, state, company, is_test, owner, expected_time_sort)

    page_objs = page.Cpt(objs, count=1000, page=page_index).info

    # 格式化json
    num = 1000 * (page_index - 1)
    data = format_uncreate_order(page_objs[0], num) if state == -1 else format_order(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'sum_price': str(sum_price or 0), 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_order')
def get_order_by_id(request):
    order_id = request.REQUEST.get('order_id')

    data = format_order([OrderBase().get_order_by_id(order_id)], 1, True)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_order')
@common_ajax_response
def distribute_order(request):
    order_id = request.POST.get('order_id')

    return OrderBase().distribute_order(order_id, request.user.id)

@verify_permission('modify_order')
@common_ajax_response
def confirm_order(request):
    order_id = request.POST.get('order_id')
    ip = utils.get_clientip(request)
    return OrderBase().confirm_order(order_id, request.user.id, ip)

@verify_permission('modify_order')
@common_ajax_response
def drop_order(request):
    order_id = request.POST.get('order_id')

    return OrderBase().drop_order(order_id)

def _get_items(item_ids, item_amounts):

    meal_items = []
    for x in range(len(item_ids)):
        meal_items.append({
            'item_id': item_ids[x],
            'amount': item_amounts[x]
        })

    return meal_items

@verify_permission('modify_order')
@common_ajax_response
def modify_order(request):
    order_id = request.POST.get('order_id')
    total_price = request.POST.get('total_price')
    is_test = request.POST.get('is_test')
    is_test = True if is_test == "1" else False
    note = request.POST.get('note')
    person_count = request.POST.get('person_count')
    owner = request.POST.get('owner')
    expected_time = request.POST.get('expected_time')
    if expected_time:
        expected_time = datetime.datetime.now().strftime('%Y-%m-%d') + ' ' + expected_time
        expected_time = datetime.datetime.strptime(expected_time, '%Y-%m-%d %H:%M')
    
    # 套餐项目
    item_ids = request.POST.getlist('item-ids')
    item_amounts = request.POST.getlist('item-amounts')

    return OrderBase().modify_order(
        order_id, _get_items(item_ids, item_amounts), total_price, 
        note, is_test, person_count, owner, expected_time
    )

@verify_permission('add_order')
@common_ajax_response
def add_order(request):
    meal_id = request.POST.get('meal')
    total_price = request.POST.get('total_price')
    is_test = request.POST.get('is_test')
    is_test = True if is_test == "1" else False
    note = request.POST.get('note')
    person_count = request.POST.get('person_count')
    create_operator = request.user.id
    owner = request.POST.get('owner')
    expected_time = request.POST.get('expected_time')
    if expected_time:
        expected_time = datetime.datetime.now().strftime('%Y-%m-%d') + ' ' + expected_time
        expected_time = datetime.datetime.strptime(expected_time, '%Y-%m-%d %H:%M')

    # 套餐项目
    item_ids = request.POST.getlist('item-ids')
    item_amounts = request.POST.getlist('item-amounts')

    flag, msg = OrderBase().add_order(
        meal_id, create_operator, total_price, 
        _get_items(item_ids, item_amounts), person_count, 
        owner, expected_time, is_test, note
    )

    return flag, msg.id if flag == 0 else msg

@verify_permission('')
def print_order(request, template_name='pc/admin/print_order.html'):
    order_id = request.REQUEST.get('order_id')

    order = OrderBase().get_order_by_id(order_id)
    # items = OrderBase().get_items_of_order(order_id)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def get_items_of_order(request):
    order_id = request.POST.get('order_id')
    data = []

    for i in OrderBase().get_items_of_order(order_id):

        supplier = SupplierBase().get_supplier_by_id(i.item.supplier_id)

        # 比佳兔超市
        show_code = True if i.order.company_id in (185, 187) else False

        data.append({
            'item_id': i.item.id,
            'name': i.item.name + (' (%s)' % i.item.des if show_code else ''),
            'price': str(i.item.price),
            'net_weight_price': str(i.item.smart_net_weight_price()),
            'sale_price': str(i.item.get_smart_sale_price()),
            'item_type': i.item.item_type,
            'item_type_str': i.item.get_item_type_display(),
            'spec': i.item.spec,
            'spec_str': i.item.get_spec_display(),
            'code': i.item.code,
            'img': i.item.img,
            'des': i.item.des,
            'smart_des': i.item.smart_des(),
            'supplier_id': supplier.id if supplier else '',
            'supplier_name': supplier.name if supplier else u'无',
            'amount': i.amount if i.item.integer == 2 else int(i.amount)
        })

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('')
def order_state(request, template_name='pc/admin/order_state.html'):
    order_id = request.REQUEST.get('order_id')
    order = OrderBase().get_order_by_id(order_id)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('modify_order')
@common_ajax_response
def modify_owner(request):
    order_id = request.POST.get('order_id')
    owner = request.POST.get('owner')

    return OrderBase().modify_owner(order_id, owner)


