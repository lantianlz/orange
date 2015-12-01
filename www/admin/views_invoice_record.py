# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.company.interface import InvoiceRecordBase, UserBase

@verify_permission('')
def invoice_record(request, template_name='pc/admin/invoice_record.html'):
    from www.company.models import InvoiceRecord
    states = [{'name': x[1], 'value': x[0]} for x in InvoiceRecord.state_choices]
    all_states = [{'value': x[0], 'name': x[1]} for x in InvoiceRecord.state_choices]
    all_states.append({'value': 0, 'name': u"全部"})

    today = datetime.datetime.now()
    start_date = (today.replace(day=1)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_record(objs, num):
    data = []

    for x in objs:
        num += 1

        operator = UserBase().get_user_by_id(x.operator)
        transporter = UserBase().get_user_by_id(x.transporter)

        data.append({
            'num': num,
            'record_id': x.id,
            'company_id': x.company.id,
            'company_name': x.company.name,
            'company_combine_name': x.company.combine_name(),
            'operator_id': operator.id if operator else '',
            'operator_name': operator.nick if operator else '',
            'invoice_amount': str(x.invoice_amount),
            'title': x.title,
            'content': x.content,
            'transporter_id': transporter.id if transporter else '',
            'transporter_name': transporter.nick if transporter else '',
            'invoice_date': str(x.invoice_date),
            'state': x.state,
            'state_str': x.get_state_display(),
            'img': x.img,
            'create_time': str(x.create_time)
        })

    return data

@verify_permission('query_invoice_record')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    state = request.REQUEST.get('state')
    state = None if state == "0" else state
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    page_index = int(request.REQUEST.get('page_index'))

    objs, sum_price = InvoiceRecordBase().search_records_for_admin(name, state, start_date, end_date)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_record(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'sum_price': str(sum_price or 0), 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )

@verify_permission('query_invoice_record')
def get_record_by_id(request):
    record_id = request.REQUEST.get('record_id')

    data = format_record([InvoiceRecordBase().get_record_by_id(record_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')

@verify_permission('add_invoice_record')
def add_record(request):
    company_id = request.POST.get('company_id')
    title = request.POST.get('title')
    invoice_amount = request.POST.get('invoice_amount')
    content = request.POST.get('content')
    invoice_date = request.POST.get('invoice_date')
    transporter = request.POST.get('transporter')

    img_name = ''
    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='invoice')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = InvoiceRecordBase().add_record(
        company_id, title, invoice_amount, content, invoice_date, request.user.id, transporter, img_name
    )

    if flag == 0:
        url = "/admin/invoice_record?#modify/%s" % (msg.id)
    else:
        url = "/admin/invoice_record?%s" % (msg)

    return HttpResponseRedirect(url)


@verify_permission('modify_invoice_record')
def modify_record(request):

    record_id = request.POST.get('record_id')
    company_id = request.POST.get('company_id')
    title = request.POST.get('title')
    invoice_amount = request.POST.get('invoice_amount')
    content = request.POST.get('content')
    invoice_date = request.POST.get('invoice_date')
    transporter = request.POST.get('transporter')
    state = request.POST.get('state')

    obj = InvoiceRecordBase().get_record_by_id(record_id)
    img_name = obj.img

    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='invoice')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = InvoiceRecordBase().modify_record(
    	record_id, company_id, title, invoice_amount, content, 
    	invoice_date, request.user.id, state, transporter, img_name
    )

    if flag == 0:
        url = "/admin/invoice_record?#modify/%s" % (obj.id)
    else:
        url = "/admin/invoice_record?%s#modify/%s" % (msg, obj.id)

    return HttpResponseRedirect(url)
