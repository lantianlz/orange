# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required

from www.company.interface import ItemBase

@verify_permission('')
def meal(request, template_name='pc/admin/meal.html'):
    from www.company.models import Item
    states = [{'name': x[1], 'value': x[0]} for x in Item.state_choices]
    types = [{'name': x[1], 'value': x[0]} for x in Item.type_choices]

    today = datetime.datetime.now()
    start_date = today.strftime('%Y-%m-%d')
    end_date = (today + datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    
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
            'state': x.state,
            'code': x.code,
            'img': x.img,
            'sort': x.sort
        })

    return data


@verify_permission('query_item')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    page_index = int(request.REQUEST.get('page_index'))

    objs = ItemBase().search_items_for_admin(name)

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
    sort = request.POST.get('sort')
    state = request.POST.get('state')
    # state = True if state == "1" else False

    return ItemBase().modify_item(item_id, name, item_type, spec, price, sort, state)

@verify_permission('add_item')
@common_ajax_response
def add_item(request):
    name = request.POST.get('name')
    item_type = request.POST.get('item_type')
    spec = request.POST.get('spec')
    price = request.POST.get('price')
    sort = request.POST.get('sort')

    flag, msg = ItemBase().add_item(name, item_type, spec, price, sort)
    return flag, msg.id if flag == 0 else msg
