# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission, log_sensitive_operation
from www.misc import qiniu_client
from common import utils, page

from www.company.interface import CompanyBase, CashRecordBase
from www.company.models import CashRecord

@verify_permission('')
def cash_record(request, template_name='pc/admin/cash_record.html'):
    operation_choices = [{'value': x[0], 'name': x[1]} for x in CashRecord.operation_choices]

    today = datetime.datetime.now()
    start_date= (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_record(objs, num):
    data = []

    for x in objs:
        num += 1

        company = CompanyBase().get_company_by_id(x.cash_account.company_id) if x.cash_account.company_id else None

        data.append({
            'num': num,
            'record_id': x.id,
            'balance': str(x.cash_account.balance),
            'company_id': company.id if company else '',
            'company_name': company.name if company else '',
            'value': str(x.value),
            'current_balance': str(x.current_balance),
            'operation': x.operation,
            'notes': x.notes,
            'ip': x.ip,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_cash_record')
def search(request):
    data = []

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    name = request.REQUEST.get('name')
    
    page_index = int(request.REQUEST.get('page_index'))
    
    objs = CashRecordBase().get_records_for_admin(start_date, end_date, name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_record(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )

@verify_permission('add_cash_record')
@log_sensitive_operation
@common_ajax_response
def add_cash_record(request):
    company_id = request.REQUEST.get('company_id')
    value = request.REQUEST.get('value')
    operation = request.REQUEST.get('operation')
    notes = request.REQUEST.get('notes')
    ip = utils.get_clientip(request)

    return CashRecordBase().add_cash_record_with_transaction(company_id, value, operation, notes, ip)

