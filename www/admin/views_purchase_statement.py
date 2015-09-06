# -*- coding: utf-8 -*-

import json
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page, cache

from www.company.interface import OrderBase, PurchaseRecordBase

@verify_permission('')
def purchase_statement(request, template_name='pc/admin/purchase_statement.html'):
    
    today = datetime.datetime.now()
    weekday = today.date().weekday()
    start_date= (today - datetime.timedelta(days=weekday)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('query_purchase_record')
def get_purchase_statement(request):
    data = {}

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    name = request.REQUEST.get('name')

    objs = OrderBase().get_purchase_statement(name, start_date, end_date)
    records = PurchaseRecordBase().get_purchase_records(name, start_date, end_date)

    for x in objs:
        key = x[0]

        # 按照供货商id 分组
        if not data.has_key(key):
            
            data[key] = {
                'supplier_id': key,
                'supplier_name': x[1],
                'order_price': 0,
                'orders': []
            }

        data[key]['order_price'] += x[2]
        data[key]['orders'].append({
            'price': str(x[2]),
            'order_no': x[3],
            'date': str(x[4]),
            'company_name': x[5],
            'order_id': x[6]
        })

    i = 0
    for x in data.values():
        i += 1
        x['num'] = i
        x['order_price'] = str(x['order_price'])
        # 拼装采购数据
        temp = [k['price__sum'] for k in records if k['supplier_id'] == x['supplier_id']]
        x['purchase_price'] = str(temp[0]) if temp else '0.00'

    return HttpResponse(
        json.dumps({'data': data}),
        mimetype='application/json'
    )