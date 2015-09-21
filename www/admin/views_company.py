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
from www.account.interface import UserBase

@verify_permission('')
def company(request, template_name='pc/admin/company.html'):
    from www.company.models import Company
    states = [{'name': x[1], 'value': x[0]} for x in Company.state_choices]
    shows = [{'name': x[1], 'value': x[0]} for x in Company.show_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_company(objs, num):
    data = []

    for x in objs:
        num += 1

        city = CityBase().get_city_by_id(x.city_id)
        invite = UserBase().get_user_by_id(x.invite_by) if x.invite_by else ''
        sale_by = UserBase().get_user_by_id(x.sale_by) if x.sale_by else ''

        data.append({
            'num': num,
            'company_id': x.id,
            'name': x.name,
            'logo': x.get_logo(),
            'des': x.des,
            'staff_name': x.staff_name,
            'mobile': x.mobile,
            'tel': x.tel,
            'addr': x.addr,
            'city_id': x.city_id,
            'city_name': city.city if city else '',
            'invite_id': invite.id if invite else '',
            'invite_name': invite.nick if invite else '',
            'person_count': x.person_count,
            'source': x.source,
            'state': x.state,
            'sort': x.sort,
            'short_name': x.short_name,
            'is_show': x.is_show,
            'sale_by_id': sale_by.id if sale_by else '',
            'sale_by_nick': sale_by.nick if sale_by else '',
            'sale_date': str(x.sale_date)[:10] if x.sale_date else '',
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
    invite = request.REQUEST.get('invite_by')
    is_show = request.REQUEST.get('is_show')
    short_name = request.REQUEST.get('short_name')
    state = request.REQUEST.get('state')
    sale_date = request.REQUEST.get('sale_date')
    sale_by = request.REQUEST.get('sale_by')

    obj = CompanyBase().get_company_by_id(company_id)
    img_name = obj.logo

    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='company')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = CompanyBase().modify_company(
        company_id, name, staff_name, mobile, tel, addr, 
        city_id, sort, des, state, person_count, invite, is_show, 
        img_name, short_name, sale_date, sale_by
    )

    if flag == 0:
        url = "/admin/company?#modify/%s" % (obj.id)
    else:
        url = "/admin/company?%s#modify/%s" % (msg, obj.id)

    return HttpResponseRedirect(url)


@verify_permission('add_company')
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
    invite = request.REQUEST.get('invite_by')
    is_show = request.REQUEST.get('is_show')
    short_name = request.REQUEST.get('short_name')
    sale_date = request.REQUEST.get('sale_date')
    sale_by = request.REQUEST.get('sale_by')

    img_name = ''
    img = request.FILES.get('img')
    if img:
        flag, img_name = qiniu_client.upload_img(img, img_type='company')
        img_name = '%s/%s' % (settings.IMG0_DOMAIN, img_name)

    flag, msg = CompanyBase().add_company(name, staff_name, 
        mobile, tel, addr, city_id, sort, des, person_count, invite, is_show, 
        img_name, short_name, sale_date, sale_by)

    if flag == 0:
        url = "/admin/company?#modify/%s" % (msg.id)
    else:
        url = "/admin/company?%s" % (msg)

    return HttpResponseRedirect(url)

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
            result.append([x.id, u'%s [%s人]' % (x.name, x.person_count), None, u'%s [%s人]' % (x.name, x.person_count)])

    return HttpResponse(json.dumps(result), mimetype='application/json')