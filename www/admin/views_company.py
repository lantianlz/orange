# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission, member_required
from www.misc import qiniu_client
from common import utils, page

from www.company.interface import CompanyBase
from www.city.interface import CityBase

@verify_permission('')
def company(request, template_name='pc/admin/company.html'):
    from www.company.models import Company
    states = [{'name': x[1], 'value': x[0]} for x in Company.state_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_company(objs, num):
    data = []

    for x in objs:
        num += 1

        city = CityBase().get_city_by_id(x.city_id)

        data.append({
            'num': num,
            'company_id': x.id,
            'name': x.name,
            'logo': x.logo,
            'des': x.des,
            'staff_name': x.staff_name,
            'mobile': x.mobile,
            'tel': x.tel,
            'addr': x.addr,
            'city_id': x.city_id,
            'city_name': city.city if city else '',
            'person_count': x.person_count,
            'source': x.source,
            'state': x.state,
            'sort': x.sort,
            'create_time': str(x.create_time)
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
    staff_name = request.REQUEST.get('staff_name')
    mobile = request.REQUEST.get('mobile')
    tel = request.REQUEST.get('tel')
    addr = request.REQUEST.get('addr')
    city_id = request.REQUEST.get('city_id')
    person_count = request.REQUEST.get('person_count')
    sort = request.REQUEST.get('sort')
    des = request.REQUEST.get('des')
    state = request.REQUEST.get('state')

    return CompanyBase().modify_company(
        company_id, name, staff_name, mobile, tel, addr, city_id, sort, des, state, person_count
    )


@verify_permission('add_company')
@common_ajax_response
def add_company(request):
    name = request.REQUEST.get('name')
    staff_name = request.REQUEST.get('staff_name')
    mobile = request.REQUEST.get('mobile')
    tel = request.REQUEST.get('tel')
    addr = request.REQUEST.get('addr')
    city_id = request.REQUEST.get('city_id')
    person_count = request.REQUEST.get('person_count')
    sort = request.REQUEST.get('sort')
    des = request.REQUEST.get('des')

    flag, msg = CompanyBase().add_company(name, staff_name, mobile, tel, addr, city_id, sort, des, person_count)

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