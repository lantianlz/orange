# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission, member_required
from www.misc import qiniu_client
from common import utils, page

from www.car_wash.interface import CompanyBase

@verify_permission('')
def company(request, template_name='pc/admin/company.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_company(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'company_id': x.id,
            'name': x.name,
            'car_wash_count': x.car_wash_count
        })

    return data


@verify_permission('query_company')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    page_index = int(request.REQUEST.get('page_index'))

    objs = CompanyBase().search_companys_for_admin(name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_company(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_company')
def get_company_by_id(request):
    company_id = request.REQUEST.get('company_id')

    data = format_company([CompanyBase().get_company_by_id(company_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_company')
@common_ajax_response
def modify_company(request):
    company_id = request.REQUEST.get('company_id')
    name = request.REQUEST.get('name')

    return CompanyBase().modify_company(
        company_id, name
    )


@verify_permission('add_company')
@common_ajax_response
def add_company(request):
    name = request.REQUEST.get('name')

    flag, msg = CompanyBase().add_company(
        name
    )

    return flag, msg.id if flag == 0 else msg

@member_required
def get_companys_by_name(request):
    '''
    根据名字查询公司
    '''
    company_name = request.REQUEST.get('company_name')

    result = []

    companys = CompanyBase().get_companys_by_name(company_name)

    if companys:
        for x in companys:
            result.append([x.id, x.name, None, x.name])

    return HttpResponse(json.dumps(result), mimetype='application/json')