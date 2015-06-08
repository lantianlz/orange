# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission, log_sensitive_operation
from www.misc import qiniu_client
from common import utils, page

from www.car_wash.interface import CarWashBase
from www.cash.interface import CarWashCashRecordBase, CarWashCashBase

@verify_permission('')
def car_wash_cash_record(request, template_name='pc/admin/car_wash_cash_record.html'):
    from www.cash.models import operation_choices
    operation_choices = [{'value': x[0], 'name': x[1]} for x in operation_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_record(objs, num):
    data = []

    for x in objs:
        num += 1

        car_wash = CarWashBase().get_car_wash_by_id(x.car_wash_cash.car_wash_id, None)

        data.append({
            'num': num,
            'record_id': x.id,
            'car_wash_id': car_wash.id,
            'car_wash_name': car_wash.name,
            'balance': str(x.car_wash_cash.balance),
            'value': str(x.value),
            'current_balance': str(x.current_balance),
            'operation': x.operation,
            'notes': x.notes,
            'ip': x.ip,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_car_wash_cash_record')
def search(request):
    data = []

    car_wash_name = request.REQUEST.get('car_wash_name')

    page_index = int(request.REQUEST.get('page_index'))

    objs = CarWashCashRecordBase().search_records_for_admin(car_wash_name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_record(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


def format_balance(objs, num):
    data = []

    for x in objs:
        num += 1

        car_wash = CarWashBase().get_car_wash_by_id(x.car_wash_id, None)

        data.append({
            'num': num,
            'balance_id': x.id,
            'car_wash_id': car_wash.id,
            'car_wash_name': car_wash.name,
            'balance': str(x.balance),
            'car_wash_bank_id': car_wash.banks.all()[0].id if car_wash.banks.all() else ''
        })

    return data

@verify_permission('query_car_wash_cash_record')
def search_balance(request):
    data = []

    car_wash_name = request.REQUEST.get('car_wash_name')

    page_index = int(request.REQUEST.get('page_index'))

    objs = CarWashCashBase().search_balances_for_admin(car_wash_name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_balance(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )

@verify_permission('add_car_wash_cash_record')
@log_sensitive_operation
@common_ajax_response
def add_record(request):
    car_wash_id = request.REQUEST.get('car_wash_id')
    value = request.REQUEST.get('value')
    operation = request.REQUEST.get('operation')
    notes = request.REQUEST.get('notes')

    return CarWashCashRecordBase().add_record_with_transaction(car_wash_id, value, operation, notes)