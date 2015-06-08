# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.car_wash.interface import CarWashBankBase

@verify_permission('')
def bank(request, template_name='pc/admin/car_wash_bank.html'):
    #choices = [{'value': x[0], 'name': x[1]} for x in group_choices]
    balance_date = datetime.datetime.now().strftime('%Y-%m') + '-05'
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_bank(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'bank_id': x.id,
            'car_wash_id': x.car_wash.id,
            'car_wash_name': x.car_wash.name,
            'manager_name': x.manager_name,
            'mobile': x.mobile,
            'tel': x.tel,
            'bank_name': x.bank_name,
            'bank_card': x.bank_card,
            'balance_date': str(x.balance_date)
        })

    return data


@verify_permission('query_car_wash_bank')
def search(request):
    data = []

    car_wash_name = request.REQUEST.get('car_wash_name')
    page_index = int(request.REQUEST.get('page_index'))

    objs = CarWashBankBase().search_banks_for_admin(car_wash_name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_bank(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_car_wash_bank')
def get_bank_by_id(request):
    bank_id = request.REQUEST.get('bank_id')

    data = format_bank([CarWashBankBase().get_bank_by_id(bank_id, None)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_car_wash_bank')
@common_ajax_response
def modify_bank(request):
    bank_id = request.REQUEST.get('bank_id')
    car_wash_id = request.REQUEST.get('car_wash_id')
    manager_name = request.REQUEST.get('manager_name')
    mobile = request.REQUEST.get('mobile')
    tel = request.REQUEST.get('tel')
    bank_name = request.REQUEST.get('bank_name')
    bank_card = request.REQUEST.get('bank_card')
    balance_date = request.REQUEST.get('balance_date')

    return CarWashBankBase().modify_bank(
        bank_id, car_wash_id, manager_name, mobile, 
        tel, bank_name, bank_card, balance_date
    )


@verify_permission('add_car_wash_bank')
@common_ajax_response
def add_bank(request):
    car_wash_id = request.REQUEST.get('car_wash_id')
    manager_name = request.REQUEST.get('manager_name')
    mobile = request.REQUEST.get('mobile')
    tel = request.REQUEST.get('tel')
    bank_name = request.REQUEST.get('bank_name')
    bank_card = request.REQUEST.get('bank_card')
    balance_date = request.REQUEST.get('balance_date')

    flag, msg = CarWashBankBase().add_bank(
        car_wash_id, manager_name, mobile, 
        tel, bank_name, bank_card, balance_date
    )

    return flag, msg.id if flag == 0 else msg