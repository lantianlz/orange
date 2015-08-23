# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission, member_required
from www.misc import qiniu_client
from common import utils, page

from www.company.interface import SupplierBase

@verify_permission('')
def supplier(request, template_name='pc/admin/supplier.html'):
    from www.company.models import Supplier
    states = [{'name': x[1], 'value': x[0]} for x in Supplier.state_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_supplier(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'supplier_id': x.id,
            'name': x.name,
            'contact': x.contact,
            'des': x.des,
            'tel': x.tel,
            'addr': x.addr,
            'state': x.state,
            'sort': x.sort,
            'bank_name': x.bank_name,
            'account_name': x.account_name,
            'account_num': x.account_num,
            'remittance_des': x.remittance_des,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_supplier')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    page_index = int(request.REQUEST.get('page_index'))

    objs = SupplierBase().search_suppliers_for_admin(name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_supplier(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_supplier')
def get_supplier_by_id(request):
    supplier_id = request.REQUEST.get('supplier_id')

    data = format_supplier([SupplierBase().get_supplier_by_id(supplier_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_supplier')
@common_ajax_response
def modify_supplier(request):
    supplier_id = request.REQUEST.get('supplier_id')
    name = request.REQUEST.get('name')
    contact = request.REQUEST.get('contact')
    tel = request.REQUEST.get('tel')
    addr = request.REQUEST.get('addr')
    sort = request.REQUEST.get('sort')
    des = request.REQUEST.get('des')
    state = request.REQUEST.get('state')
    bank_name = request.REQUEST.get('bank_name')
    account_name = request.REQUEST.get('account_name')
    account_num = request.REQUEST.get('account_num')
    remittance_des = request.REQUEST.get('remittance_des')

    return SupplierBase().modify_supplier(
        supplier_id, name, contact, tel, addr, bank_name, account_name, 
        account_num, state, sort, des, remittance_des
    )


@verify_permission('add_supplier')
@common_ajax_response
def add_supplier(request):
    name = request.REQUEST.get('name')
    contact = request.REQUEST.get('contact')
    tel = request.REQUEST.get('tel')
    addr = request.REQUEST.get('addr')
    sort = request.REQUEST.get('sort')
    des = request.REQUEST.get('des')
    bank_name = request.REQUEST.get('bank_name')
    account_name = request.REQUEST.get('account_name')
    account_num = request.REQUEST.get('account_num')
    remittance_des = request.REQUEST.get('remittance_des')

    flag, msg = SupplierBase().add_supplier(
        name, contact, tel, addr, bank_name, 
        account_name, account_num, sort, des, remittance_des
    )

    return flag, msg.id if flag == 0 else msg

@member_required
def get_suppliers_by_name(request):
    '''
    根据名字查询供货商
    '''
    supplier_name = request.REQUEST.get('supplier_name')

    result = []

    suppliers = SupplierBase().get_suppliers_by_name(supplier_name)

    if suppliers:
        for x in suppliers:
            result.append([x.id, x.name, None, x.name])

    return HttpResponse(json.dumps(result), mimetype='application/json')