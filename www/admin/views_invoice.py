# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from common import utils, page
from www.misc import qiniu_client
from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required, log_sensitive_operation

from www.company.interface import InvoiceBase, CompanyBase

@verify_permission('')
def invoice(request, template_name='pc/admin/invoice.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_invoice(objs, num):
    data = []

    for x in objs:
        num += 1

        company = CompanyBase().get_company_by_id(x.company_id)

        data.append({
            'num': num,
            'invoice_id': x.id,
            'company_id': company.id,
            'company_name': company.name,
            'company_combine_name': company.combine_name(),
            'title': x.title,
            'content': x.content,
        })

    return data

@verify_permission('query_invoice')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    page_index = int(request.REQUEST.get('page_index'))

    objs = InvoiceBase().search_invoices_for_admin(name)

    page_objs = page.Cpt(objs, count=20, page=page_index).info

    # 格式化json
    num = 20 * (page_index - 1)
    data = format_invoice(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )

@verify_permission('query_invoice')
def get_invoice_by_id(request):
    invoice_id = request.REQUEST.get('invoice_id')

    data = format_invoice([InvoiceBase().get_invoice_by_id(invoice_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


def get_invoice_by_company_id(request):
    company_id = request.REQUEST.get('company_id')

    data = {
        'title': '',
        'content': u'水果和点心'
    }

    result = InvoiceBase().get_invoice_by_company_id(company_id)
    if result and result.title:
        data['title'] = result.title
    else:
        company = CompanyBase().get_company_by_id(company_id)
        data['title'] = company.name

    if result and result.content:
        data['content'] = result.content

    return HttpResponse(json.dumps(data), mimetype='application/json')

@verify_permission('add_invoice')
@common_ajax_response
def add_invoice(request):
    company = request.POST.get('company')
    title = request.POST.get('title')
    content = request.POST.get('content')

    flag, msg = InvoiceBase().add_invoice(
        company, title, content
    )
    return flag, msg.id if flag == 0 else msg


@verify_permission('modify_invoice')
@common_ajax_response
def modify_invoice(request):
    invoice_id = request.POST.get('invoice_id')
    company = request.POST.get('company')
    title = request.POST.get('title')
    content = request.POST.get('content')

    return InvoiceBase().modify_invoice(
        invoice_id, company, title, content
    )
