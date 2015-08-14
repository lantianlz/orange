# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.company.models import Order, Item
from www.company.interface import OrderBase, MealBase, CompanyBase
from www.account.interface import UserBase

@verify_permission('')
def order(request, template_name='pc/admin/order.html'):
    states = [{'value': x[0], 'name': x[1]} for x in Order.state_choices]
    all_states = [{'value': x[0], 'name': x[1]} for x in Order.state_choices]
    all_states.insert(0, {'value': -1, 'name': u"待创建"})
    all_states.append({'value': -2, 'name': u"全部有效订单"})

    today = datetime.datetime.now()
    start_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_order(objs, num):
    data = []

    for x in objs:
        num += 1

        meal = MealBase().get_meal_by_id(x.meal_id)
        company = CompanyBase().get_company_by_id(x.company_id)
        create_operator = UserBase().get_user_by_id(x.create_operator)
        distribute_operator = UserBase().get_user_by_id(x.distribute_operator) if x.distribute_operator else ''
        confirm_operator = UserBase().get_user_by_id(x.confirm_operator) if x.confirm_operator else ''

        data.append({
            'num': num,
            'order_id': x.id,
            'meal_id': meal.id,
            'meal_name': u'%s [¥%s]' % (meal.name, meal.price),
            'company_id': company.id,
            'company_name': company.name,
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
            'note': x.note,
            'rate': x.rate(),
            'is_test': x.is_test,
            'state': x.state
        })

    return data

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
            'company_name': company.name,
            'order_no': '',
            'create_time': '',
            'total_price': '',
            'is_test': '',
            'state': -1
        })

    return data

@verify_permission('query_order')
def search(request):
    data = []

    start_date = request.POST.get('start_date')
    start_date = start_date or datetime.datetime.now().strftime('%Y-%m-%d')
    start_date += " 00:00:00"
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date = request.POST.get('end_date', datetime.datetime.now().strftime('%Y-%m-%d'))
    end_date = end_date or datetime.datetime.now().strftime('%Y-%m-%d')
    end_date += " 23:59:59"
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    state = request.POST.get('state', '-1')
    state = int(state)
    order_no = request.POST.get('order_no')
    
    page_index = int(request.REQUEST.get('page_index'))

    if state == -1:
        objs = OrderBase().search_uncreate_orders_for_admin(start_date, end_date)
    else:
        objs = OrderBase().search_orders_for_admin(start_date, end_date, state, order_no)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_uncreate_order(page_objs[0], num) if state == -1 else format_order(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_order')
def get_order_by_id(request):
    order_id = request.REQUEST.get('order_id')

    data = format_order([OrderBase().get_order_by_id(order_id)], 1)[0]

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

    return OrderBase().confirm_order(order_id, request.user.id)

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

@verify_permission('add_order')
@common_ajax_response
def add_order(request):
    meal_id = request.POST.get('meal')
    total_price = request.POST.get('total_price')
    is_test = request.POST.get('is_test')
    is_test = True if is_test == "1" else False
    note = request.POST.get('note')
    create_operator = request.user.id

    # 套餐项目
    item_ids = request.POST.getlist('item-ids')
    item_amounts = request.POST.getlist('item-amounts')

    flag, msg = OrderBase().add_order(
        meal_id, create_operator, total_price, 
        _get_items(item_ids, item_amounts), is_test, note
    )

    return flag, msg.id if flag == 0 else msg

@verify_permission('')
def print_order(request, template_name='pc/admin/print_order.html'):
    order_id = request.REQUEST.get('order_id')

    order = OrderBase().get_order_by_id(order_id)
    items = OrderBase().get_items_of_order(order_id)

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
            'type': item.item.get_item_type_display
        })

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('query_order')
def purchase(request, template_name='pc/admin/purchase.html'):
    states = [{'value': x[0], 'name': x[1]} for x in Order.state_choices if x[0] != 0]
    states.append({'value': -2, 'name': u"全部有效订单"})
    
    types_json = json.dumps(dict(Item.type_choices))
    specs_json = json.dumps(dict(Item.spec_choices))
    types = [{'value': x[0], 'name': x[1]} for x in Item.type_choices]

    today = datetime.datetime.now()
    start_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def _get_purchase_data(start_date, end_date, state, show_order=False):

    start_date = start_date or datetime.datetime.now().strftime('%Y-%m-%d')
    start_date += " 00:00:00"
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date = end_date or datetime.datetime.now().strftime('%Y-%m-%d')
    end_date += " 23:59:59"
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    state = int(state)

    data = OrderBase().get_purchase(start_date, end_date, state)

    result = {}
    for x in data:

        key = x['item__code']
        order_key = x['order__order_no']

        if not result.has_key(key):
            result[key] = {
                'code': x['item__code'],
                'name': x['item__name'],
                'amount': 0,
                'spec': x['item__spec'],
                'item_type': x['item__item_type'],
                'orders': {}
            }

        # 汇总数量
        result[key]['amount'] += x['amount']

        if show_order:
            if not result[key]['orders'].has_key(order_key):
                result[key]['orders'][order_key] = {
                    'order_no': order_key,
                    'company': x['order__company__name'],
                    'amount': x['amount']
                }

    return result.values()


@verify_permission('query_order')
def get_purchase(request):

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    state = request.POST.get('state', '-1')

    data = _get_purchase_data(start_date, end_date, state, True)

    return HttpResponse(json.dumps(data), mimetype='application/json')

@verify_permission('')
def print_purchase(request, template_name='pc/admin/print_purchase.html'):
    types_json = json.dumps(dict(Item.type_choices))
    specs_json = json.dumps(dict(Item.spec_choices))
    types = [{'value': x[0], 'name': x[1]} for x in Item.type_choices]

    start_date = request.REQUEST.get('start_date')
    end_date = request.REQUEST.get('end_date')
    state = request.REQUEST.get('state', '-1')

    data = _get_purchase_data(start_date, end_date, state)
    data_json = json.dumps(data)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

