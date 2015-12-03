# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.company.interface import InvoiceRecordBase, UserBase, CashRecordBase, CompanyBase, CashAccountBase

@verify_permission('')
def invoice_statement(request, template_name='pc/admin/invoice_statement.html'):
    today = datetime.datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    start_date = datetime.datetime(2015, 8, 1).strftime('%Y-%m-%d')[:10]
    end_date = today.strftime('%Y-%m-%d')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('')
def get_invoice_statement(request):
    data = [
        {'name': u'成都咕咚科技有限公司', 'account': '3000', 'recharge': 10000, 'invoice_amount': 20000 },
        {'name': u'成都咕咚科技有限公司', 'account': '5000', 'recharge': 30000, 'invoice_amount': 40000 }
    ]

    company_name = request.REQUEST.get('name')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)

    data = {}

    # 发票金额数据
    invoice_record_data = InvoiceRecordBase().get_invoice_amount_group_by_company(company_name, start_date, end_date)

    # 充值金额数据
    recharge_data = CashRecordBase().get_records_group_by_company(start_date, end_date, 0, 1)
    recharge_dict = {}
    for x in recharge_data:
        recharge_dict[x['cash_account__company_id']] = str(x['recharge'])

    # 公司数据
    company_data = CompanyBase().get_all_company(1).values('id', 'name', 'short_name')
    company_dict = {}
    for x in company_data:
        company_dict[x['id']] = [x['name'], '%s [ %s ]' % (x['name'], x['short_name'] or '-')]

    # 公司现金账户
    account_data = CashAccountBase().get_all_accounts().values('company_id', 'balance')
    account_dict = {}
    for x in account_data:
        account_dict[x['company_id']] = str(x['balance'])

    for x in invoice_record_data:
        key = x['company_id']
        data[key] = {
            'name': company_dict[key][0],
            'combine_name': company_dict[key][1],
            'account': account_dict.get(key, 0),
            'recharge': recharge_dict.get(key, 0),
            'invoice_amount': str(x['invoice_amount']),
            'offset_abs': abs(float(recharge_dict.get(key, 0)) - float(x['invoice_amount'])),
            'offset': float(recharge_dict.get(key, 0)) - float(x['invoice_amount'])
        }

    data = data.values()
    # 排序 需要提醒的排列在前面
    data.sort(key=lambda x:x['offset_abs'], reverse=True)

    return HttpResponse(
        json.dumps({'data': data}),
        mimetype='application/json'
    )


