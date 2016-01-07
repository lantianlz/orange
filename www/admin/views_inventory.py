# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.company.interface import InventoryBase

@verify_permission('')
def inventory(request, template_name='pc/admin/inventory.html'):
    from www.company.models import Inventory

    states = [{'value': x[0], 'name': x[1]} for x in Inventory.state_choices]
    all_states = [{'value': x[0], 'name': x[1]} for x in Inventory.state_choices]
    all_states.append({'value': -1, 'name': u"全部"})
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_inventory(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'inventory_id': x.id,
            'item_id': x.item.id,
            'item_name': x.item.name,
            'amount': x.amount,
            'warning_value': x.warning_value,
            'state': x.state,
            'create_time': str(x.create_time)
        })

    return data

@verify_permission('query_inventory')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    state = request.REQUEST.get('state', '-1')
    state = None if state == "-1" else int(state)
    page_index = int(request.REQUEST.get('page_index'))

    objs = InventoryBase().search_inventorys_for_admin(name, state)

    page_objs = page.Cpt(objs, count=20, page=page_index).info

    # 格式化json
    num = 20 * (page_index - 1)
    data = format_inventory(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )

@verify_permission('query_inventory')
def get_inventory_by_id(request):
    inventory_id = request.REQUEST.get('inventory_id')

    data = format_inventory([InventoryBase().get_inventory_by_id(inventory_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


def get_inventorys_by_name(request):
    '''
    根据名字查询库存产品
    '''
    name = request.REQUEST.get('name')

    result = []

    inventorys = InventoryBase().get_inventorys_by_name(name)[:10]

    if inventorys:
        for x in inventorys:
            result.append([x.id, u'%s' % (x.item.name), None, u'%s' % (x.item.name)])

    return HttpResponse(json.dumps(result), mimetype='application/json')


@verify_permission('modify_inventory')
@common_ajax_response
def modify_inventory(request):
    inventory_id = request.REQUEST.get('inventory_id')
    amount = request.REQUEST.get('amount')
    warning_value = request.REQUEST.get('warning_value')
    state = request.REQUEST.get('state')

    return InventoryBase().modify_inventory(
        inventory_id, amount, warning_value, state
    )


@verify_permission('add_inventory')
@common_ajax_response
def add_inventory(request):
    item_id = request.REQUEST.get('item')
    amount = request.REQUEST.get('amount')
    warning_value = request.REQUEST.get('warning_value')
    state = request.REQUEST.get('state')

    flag, msg = InventoryBase().add_inventory(
        item_id, amount, warning_value
    )

    return flag, msg.id if flag == 0 else msg