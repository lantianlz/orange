# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from common import utils, page
from www.misc import qiniu_client
from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required, log_sensitive_operation

from www.company.interface import ItemBase, SupplierBase

@verify_permission('')
def item(request, template_name='pc/admin/item.html'):
    from www.company.models import Item
    states = [{'name': x[1], 'value': x[0]} for x in Item.state_choices]
    all_states = [{'name': x[1], 'value': x[0]} for x in Item.state_choices]
    all_states.insert(0, {'value': -1, 'name': u"全部"})
    types = [{'name': x[1], 'value': x[0]} for x in Item.type_choices]
    all_types = [{'name': x[1], 'value': x[0]} for x in Item.type_choices]
    all_types.insert(0, {'value': -1, 'name': u"全部"})
    specs = [{'name': x[1], 'value': x[0]} for x in Item.spec_choices]
    integers = [{'name': x[1], 'value': x[0]} for x in Item.integer_choices]
    init_adds = [{'name': x[1], 'value': x[0]} for x in Item.add_choices]
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_item(objs, num):
    data = []

    for x in objs:
        num += 1

        supplier = SupplierBase().get_supplier_by_id(x.supplier_id) if x.supplier_id else None

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
            'img': x.get_img(),
            'integer': x.integer,
            'sale_price': str(x.sale_price),
            'init_add': x.init_add,
            'des': x.des,
            'smart_des': x.smart_des(),
            'supplier_id': supplier.id if supplier else '',
            'supplier_name': supplier.name if supplier else '',
            'sort': x.sort
        })

    return data


@verify_permission('query_item')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    supplier = request.REQUEST.get('supplier')
    item_type = request.REQUEST.get('item_type')
    item_type = int(item_type)
    state = request.REQUEST.get('state', '-1')
    state = [] if state == "-1" else [int(state)]
    page_index = int(request.REQUEST.get('page_index'))

    objs = ItemBase().search_items_for_admin(item_type, state, supplier, name)

    page_objs = page.Cpt(objs, count=20, page=page_index).info

    # 格式化json
    num = 20 * (page_index - 1)
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
@log_sensitive_operation
def modify_item(request):

    item_id = request.POST.get('item_id')
    name = request.POST.get('name')
    item_type = request.POST.get('item_type')
    spec = request.POST.get('spec')
    price = request.POST.get('price')
    integer = request.POST.get('integer')
    init_add = request.POST.get('init_add')
    sale_price = request.POST.get('sale_price')
    sort = request.POST.get('sort')
    state = request.POST.get('state')
    supplier_id = request.POST.get('supplier_id')
    des = request.POST.get('des')

    obj = ItemBase().get_item_by_id(item_id)
    img_name = obj.img

    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='item')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = ItemBase().modify_item(item_id, name, item_type, spec, 
        price, sort, state, integer, sale_price, init_add, supplier_id, des, img_name
    )

    if flag == 0:
        url = "/admin/item?#modify/%s" % (obj.id)
    else:
        url = "/admin/item?%s#modify/%s" % (msg, obj.id)

    return HttpResponseRedirect(url)


@verify_permission('add_item')
def add_item(request):
    name = request.POST.get('name')
    item_type = request.POST.get('item_type')
    spec = request.POST.get('spec')
    price = request.POST.get('price')
    sort = request.POST.get('sort')
    integer = request.POST.get('integer')
    init_add = request.POST.get('init_add')
    sale_price = request.POST.get('sale_price')
    supplier_id = request.POST.get('supplier_id')
    des = request.POST.get('des')

    img_name = ''
    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='item')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = ItemBase().add_item(
        name, item_type, spec, price, sort, integer, 
        sale_price, init_add, supplier_id, des, img_name
    )

    if flag == 0:
        url = "/admin/item?#modify/%s" % (msg.id)
    else:
        url = "/admin/item?%s" % (msg)

    return HttpResponseRedirect(url)


@verify_permission('query_item')
def get_items_by_name(request):
    name = request.REQUEST.get('name')

    data = format_item(ItemBase().get_items_by_name(name)[:10], 1)

    return HttpResponse(json.dumps(data), mimetype='application/json')

@verify_permission('query_item')
def get_items_by_name_for_combox(request):
    '''
    根据名字查询套餐
    '''
    name = request.REQUEST.get('name')

    result = []

    items = ItemBase().get_items_by_name(name)[:10]

    if items:
        for x in items:
            result.append([x.id, u'%s' % (x.name), None, u'%s' % (x.name)])

    return HttpResponse(json.dumps(result), mimetype='application/json')

def get_item_types(request):
    from www.company.models import Item

    types = [{'name': x[1], 'value': x[0]} for x in Item.type_choices]

    return HttpResponse(json.dumps(types), mimetype='application/json')