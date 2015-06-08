# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.car_wash.models import group_choices
from www.car_wash.interface import ServiceTypeBase

@verify_permission('')
def service_type(request, template_name='pc/admin/service_type.html'):
    choices = [{'value': x[0], 'name': x[1]} for x in group_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_type(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'type_id': x.id,
            'name': x.name,
            'group_id': x.group,
            'sort_num': x.sort_num,
            'state': x.state
        })

    return data


@verify_permission('query_service_type')
def search(request):
    data = []

    page_index = int(request.REQUEST.get('page_index'))

    objs = ServiceTypeBase().search_types_for_admin()

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_type(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_service_type')
def get_service_type_by_id(request):
    type_id = request.REQUEST.get('type_id')

    data = format_type([ServiceTypeBase().get_service_type_by_id(type_id, None)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_service_type')
@common_ajax_response
def modify_service_type(request):
    type_id = request.REQUEST.get('type_id')
    name = request.REQUEST.get('name')
    sort_num = int(request.REQUEST.get('sort'))
    state = request.REQUEST.get('state')
    state = True if state == "1" else False

    return ServiceTypeBase().modify_service_type(
        type_id, name, sort_num, state
    )


@verify_permission('add_service_type')
@common_ajax_response
def add_service_type(request):
    name = request.REQUEST.get('name')
    sort_num = int(request.REQUEST.get('sort'))

    flag, msg = ServiceTypeBase().add_service_type(
        name, sort_num
    )

    return flag, msg.id if flag == 0 else msg