# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission, member_required
from www.misc import qiniu_client
from common import utils, page

from www.company.interface import CompanyBase, CashAccountBase

@verify_permission('')
def cash_account(request, template_name='pc/admin/cash_account.html'):
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_account(objs, num):
    data = []

    for x in objs:
        num += 1

        company = CompanyBase().get_company_by_id(x.company_id) if x.company_id else None

        data.append({
            'num': num,
            'account_id': x.id,
            'balance': str(x.balance),
            'company_id': company.id if company else '',
            'company_name': company.name if company else '',
            'overdraft': str(x.max_overdraft)
        })

    return data


@verify_permission('query_cash_account')
def search(request):
    data = []

    company_name = request.REQUEST.get('company_name')
    
    page_index = int(request.REQUEST.get('page_index'))

    objs = CashAccountBase().get_accounts_for_admin(company_name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_account(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_cash_account')
def get_cash_account_by_id(request):
    account_id = request.REQUEST.get('account_id')

    data = format_account([CashAccountBase().get_cash_account_by_id(account_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_cash_account')
@common_ajax_response
def modify_cash_account(request):
    account_id = request.POST.get('account_id')
    max_overdraft = request.POST.get('overdraft')

    return CashAccountBase().modify_cash_account(account_id, max_overdraft)

    