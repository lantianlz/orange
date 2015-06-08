# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.car_wash.interface import CompanyManagerBase
from www.account.interface import UserBase

@verify_permission('')
def manager(request, template_name='pc/admin/company_manager.html'):

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_manager(objs, num):
    data = []

    for x in objs:
        num += 1

        user = UserBase().get_user_by_id(x.user_id) if x.user_id else None

        data.append({
            'num': num,
            'manager_id': x.id,
            'user_id': x.user_id if user else '',
            'user_nick': user.nick if user else '',
            'company_id': x.company.id if x.company else '',
            'company_name': x.company.name if x.company else '',
            'role': x.role
        })

    return data


@verify_permission('query_company_manager')
def search(request):
    data = []

    company_name = request.REQUEST.get('company_name')
    
    page_index = int(request.REQUEST.get('page_index'))

    objs = CompanyManagerBase().search_managers_for_admin(company_name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_manager(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_company_manager')
def get_manager_by_id(request):
    manager_id = request.REQUEST.get('manager_id')

    data = format_manager([CompanyManagerBase().get_manager_by_id(manager_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')

@verify_permission('add_company_manager')
@common_ajax_response
def add_manager(request):
    company_id = request.REQUEST.get('company_id')
    manager = request.REQUEST.get('manager')

    flag, msg = CompanyManagerBase().add_company_manager(
        company_id, manager
    )

    return flag, msg.id if flag == 0 else msg


@verify_permission('remove_company_manager')
@common_ajax_response
def delete_manager(request):
    manager_id = request.REQUEST.get('manager_id')

    return CompanyManagerBase().delete_company_manager(manager_id)