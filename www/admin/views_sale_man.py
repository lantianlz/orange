# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response, verify_permission

from www.company.interface import SaleManBase
from www.account.interface import UserBase

@verify_permission('')
def sale_man(request, template_name='pc/admin/sale_man.html'):

    from www.company.models import SaleMan
    states = [{'name': x[1], 'value': x[0]} for x in SaleMan.state_choices]

    today = datetime.datetime.now().strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_sale_man(objs, num):
    data = []

    for x in objs:
        num += 1

        user = UserBase().get_user_by_id(x.user_id)

        data.append({
            'num': num,
            'sale_man_id': x.id,
            'user_id': user.id if user else '',
            'nick': user.nick if user else '',
            'employee_date': str(x.employee_date)[:10],
            'state': x.state
        })

    return data

@verify_permission('query_sale_man')
def search(request):
    data = []

    state = request.REQUEST.get('state')
    page_index = int(request.REQUEST.get('page_index'))

    objs = SaleManBase().search_sale_man_for_admin(state)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_sale_man(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )

@verify_permission('query_sale_man')
def get_sale_man_by_id(request):
    sale_man_id = request.REQUEST.get('sale_man_id')

    data = format_sale_man([SaleManBase().get_sale_man_by_id(sale_man_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')

@verify_permission('add_sale_man')
@common_ajax_response
def add_sale_man(request):
    user_id = request.REQUEST.get('user_id')
    employee_date = request.REQUEST.get('employee_date')

    flag, msg = SaleManBase().add_sale_man(user_id, employee_date)

    return flag, msg.id if flag == 0 else msg


@verify_permission('modify_sale_man')
@common_ajax_response
def modify_sale_man(request):
    sale_man_id = request.REQUEST.get('sale_man_id')
    user_id = request.REQUEST.get('user_id')
    employee_date = request.REQUEST.get('employee_date')
    state = request.REQUEST.get('state')

    return SaleManBase().modify_sale_man(sale_man_id, user_id, employee_date, state)


