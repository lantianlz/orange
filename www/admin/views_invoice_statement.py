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

    company_name = request.REQUEST.get('name')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)

    data, sum_price = InvoiceRecordBase().get_invoice_statement(company_name, start_date, end_date)

    return HttpResponse(
        json.dumps({'data': data, 'sum_price': sum_price}),
        mimetype='application/json'
    )


