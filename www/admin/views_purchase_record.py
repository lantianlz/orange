# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.company.models import PurchaseRecord
from www.company.interface import PurchaseRecordBase
from www.account.interface import UserBase

@verify_permission('')
def purchase_record(request, template_name='pc/admin/purchase_record.html'):
    states = [{'value': x[0], 'name': x[1]} for x in PurchaseRecord.state_choices]

    today = datetime.datetime.now()
    weekday = today.date().weekday()
    start_date= (today - datetime.timedelta(days=weekday)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_record(objs, num):
    data = []

    for x in objs:
        num += 1

        operator = UserBase().get_user_by_id(x.operator)

        data.append({
            'num': num,
            'record_id': x.id,
            'supplier_id': x.supplier.id,
            'supplier_name': x.supplier.name,
            'operator_id': operator.id if operator else '',
            'operator_name': operator.nick if operator else '',
            'price': str(x.price),
            'des': x.des,
            'state': x.state,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_purchase_record')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    state = request.REQUEST.get('state')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    page_index = int(request.REQUEST.get('page_index'))

    objs = PurchaseRecordBase().search_records_for_admin(name, state, start_date, end_date)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_record(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_purchase_record')
def get_record_by_id(request):
    record_id = request.REQUEST.get('record_id')

    data = format_record([PurchaseRecordBase().get_record_by_id(record_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('add_purchase_record')
@common_ajax_response
def add_record(request):
    supplier_id = request.POST.get('supplier_id')
    price = request.POST.get('price')
    des = request.POST.get('des')

    flag, msg = PurchaseRecordBase().add_record(
        supplier_id, des, price, request.user.id, utils.get_clientip(request)
    )

    return flag, msg.id if flag == 0 else msg


@verify_permission('modify_purchase_record')
@common_ajax_response
def modify_record(request):
    record_id = request.REQUEST.get('record_id')

    return PurchaseRecordBase().modify_record(record_id, utils.get_clientip(request))










