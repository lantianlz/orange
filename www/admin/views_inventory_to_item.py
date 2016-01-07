# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.company.interface import InventoryToItemBase

@verify_permission('')
def inventory_to_item(request, template_name='pc/admin/inventory_to_item.html'):
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_relationship(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'relationship_id': x.id,
            'inventory_id': x.inventory.id,
            'inventory_name': x.inventory.item.name,
            'item_id': x.item.id,
            'item_name': x.item.name,
            'amount': x.amount,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_inventory_to_item')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    page_index = int(request.REQUEST.get('page_index'))

    objs = InventoryToItemBase().search_relationship_for_admin(name)

    page_objs = page.Cpt(objs, count=20, page=page_index).info

    # 格式化json
    num = 20 * (page_index - 1)
    data = format_relationship(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_inventory_to_item')
def get_relationship_by_id(request):
    relationship_id = request.REQUEST.get('relationship_id')

    data = format_relationship([InventoryToItemBase().get_relationship_by_id(relationship_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_inventory_to_item')
@common_ajax_response
def drop_relationship(request):
    relationship_id = request.REQUEST.get('relationship_id')

    return InventoryToItemBase().drop_relationship(
        relationship_id
    )


@verify_permission('add_inventory_to_item')
@common_ajax_response
def add_relationship(request):
    item_id = request.REQUEST.get('item')
    inventory_id = request.REQUEST.get('inventory')
    amount = request.REQUEST.get('amount')

    flag, msg = InventoryToItemBase().add_relationship(
        inventory_id, item_id, amount
    )

    return flag, msg.id if flag == 0 else msg
