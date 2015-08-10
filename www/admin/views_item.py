# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required

from www.company.interface import ItemBase

@verify_permission('')
def item(request, template_name='pc/admin/item.html'):
    from www.company.models import Item
    states = [{'name': x[1], 'value': x[0]} for x in Item.state_choices]
    types = [{'name': x[1], 'value': x[0]} for x in Item.type_choices]
    all_types = [{'name': x[1], 'value': x[0]} for x in Item.type_choices]
    all_types.insert(0, {'value': -1, 'name': u"全部"})
    specs = [{'name': x[1], 'value': x[0]} for x in Item.spec_choices]
    integers = [{'name': x[1], 'value': x[0]} for x in Item.integer_choices]
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_item(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'item_id': x.id,
            'name': x.name,
            'price': str(x.price),
            'item_type': x.item_type,
            'spec': x.spec,
            'spec_text': x.get_spec_display(),
            'state': x.state,
            'code': x.code,
            'img': x.img,
            'integer': x.integer,
            'sale_price': str(x.sale_price),
            'sort': x.sort
        })

    return data


@verify_permission('query_item')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    item_type = request.REQUEST.get('item_type')
    item_type = int(item_type)
    page_index = int(request.REQUEST.get('page_index'))

    objs = ItemBase().search_items_for_admin(item_type, name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_item(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_item')
def get_item_by_id(request):
    item_id = request.REQUEST.get('item_id')

    data = format_item([ItemBase().get_item_by_id(item_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_item')
@common_ajax_response
def modify_item(request):

    item_id = request.POST.get('item_id')
    name = request.POST.get('name')
    item_type = request.POST.get('item_type')
    spec = request.POST.get('spec')
    price = request.POST.get('price')
    integer = request.POST.get('integer')
    sale_price = request.POST.get('sale_price')
    sort = request.POST.get('sort')
    state = request.POST.get('state')
    # state = True if state == "1" else False

    return ItemBase().modify_item(item_id, name, item_type, spec, price, sort, state, integer, sale_price)

@verify_permission('add_item')
@common_ajax_response
def add_item(request):
    name = request.POST.get('name')
    item_type = request.POST.get('item_type')
    spec = request.POST.get('spec')
    price = request.POST.get('price')
    sort = request.POST.get('sort')
    integer = request.POST.get('integer')
    sale_price = request.POST.get('sale_price')

    flag, msg = ItemBase().add_item(name, item_type, spec, price, sort, integer, sale_price)
    return flag, msg.id if flag == 0 else msg

@verify_permission('query_item')
def get_items_by_name(request):
    name = request.REQUEST.get('name')

    data = format_item(ItemBase().get_items_by_name(name)[:10], 1)

    return HttpResponse(json.dumps(data), mimetype='application/json')