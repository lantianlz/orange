# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from common import utils, page

from www.company.models import ParttimePerson
from www.company.interface import ParttimePersonBase

@verify_permission('')
def parttime_person(request, template_name='pc/admin/parttime_person.html'):
    states = [{'value': x[0], 'name': x[1]} for x in ParttimePerson.state_choices]
    genders = [{'value': x[0], 'name': x[1]} for x in ParttimePerson.gender_choices]

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

def format_person(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'person_id': x.id,
            'name': x.name,
            'gender': x.gender,
            'age': x.age,
            'tel': x.tel,
            'hourly_pay': x.hourly_pay,
            'note': x.note,
            'state': x.state,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_parttime_person')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    state = request.REQUEST.get('state', '1')
    state = int(state)
    page_index = int(request.REQUEST.get('page_index'))

    objs = ParttimePersonBase().search_person_for_admin(state, name)

    page_objs = page.Cpt(objs, count=20, page=page_index).info

    # 格式化json
    num = 20 * (page_index - 1)
    data = format_person(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_parttime_person')
def get_person_by_id(request):
    person_id = request.REQUEST.get('person_id')

    data = format_person([ParttimePersonBase().get_person_by_id(person_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_parttime_person')
@common_ajax_response
def modify_person(request):
    person_id = request.REQUEST.get('person_id')
    name = request.REQUEST.get('name')
    gender = request.REQUEST.get('gender')
    age = request.REQUEST.get('age')
    tel = request.REQUEST.get('tel')
    hourly_pay = request.REQUEST.get('hourly_pay')
    state = request.REQUEST.get('state')
    note = request.REQUEST.get('note')

    return ParttimePersonBase().modify_person(
        person_id, name, gender, age, tel, hourly_pay, state, note
    )


@verify_permission('add_parttime_person')
@common_ajax_response
def add_person(request):
    name = request.REQUEST.get('name')
    gender = request.REQUEST.get('gender')
    age = request.REQUEST.get('age')
    tel = request.REQUEST.get('tel')
    hourly_pay = request.REQUEST.get('hourly_pay')
    state = request.REQUEST.get('state')
    note = request.REQUEST.get('note')

    flag, msg = ParttimePersonBase().add_person(
        name, gender, age, tel, hourly_pay, state, note
    )

    return flag, msg.id if flag == 0 else msg


def get_persons_by_name(request):
    '''
    根据名字查询公司
    '''
    name = request.REQUEST.get('name')

    result = []

    persons = ParttimePersonBase().get_persons_by_name(name)

    if persons:
        for x in persons:
            result.append([x.id, x.name, None, x.name])

    return HttpResponse(json.dumps(result), mimetype='application/json')






