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

    type_dict = dict(Item.type_choices)
    spec_dict = dict(Item.spec_choices)

    start_date, end_date = utils.get_date_range(start_date, end_date)
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
                'des': x['item__des'],
                'smart_des': ('('+x['item__des']+')') if x['item__des'] else '',
                'spec': x['item__spec'],
                'spec_str': spec_dict[x['item__spec']],
                'item_type': x['item__item_type'],
                'item_type_str': type_dict[x['item__item_type']],
                'supplier_id': x['item__supplier__id'],
                'supplier_name': x['item__supplier__name'],
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

    data = result.values()

    data.sort(key=lambda x: x['supplier_id'])

    return data


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
