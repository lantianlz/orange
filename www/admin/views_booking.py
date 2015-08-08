# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required

from www.company.interface import BookingBase
from www.account.interface import UserBase

@verify_permission('')
def booking(request, template_name='pc/admin/booking.html'):
    from www.company.models import Booking
    states = [{'name': x[1], 'value': x[0]} for x in Booking.state_choices]
    sources = [{'name': x[1], 'value': x[0]} for x in Booking.source_choices]
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_booking(objs, num):
    data = []

    for x in objs:
        num += 1

        user = UserBase().get_user_by_id(x.operator_id) if x.operator_id else ''
        invite = UserBase().get_user_by_id(x.invite_by) if x.invite_by else ''

        data.append({
            'num': num,
            'booking_id': x.id,
            'company_name': x.company_name,
            'staff_name': x.staff_name,
            'mobile': x.mobile,
            'source': x.source,
            'invite_id': invite.id if invite else '',
            'invite_name': invite.nick if invite else '',
            'state': x.state,
            'operator_id': user.id if user else '',
            'operator_name': user.nick if user else '',
            'operation_time': str(x.operation_time or ''),
            'note': x.note,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_booking')
def search(request):
    data = []

    state = request.REQUEST.get('state')
    page_index = int(request.REQUEST.get('page_index'))

    objs = BookingBase().search_bookings_for_admin(state)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_booking(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_booking')
def get_booking_by_id(request):
    booking_id = request.REQUEST.get('booking_id')

    data = format_booking([BookingBase().get_booking_by_id(booking_id)], 1)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_booking')
@common_ajax_response
def modify_booking(request):

    booking_id = request.POST.get('booking_id')
    note = request.POST.get('note')
    state = request.POST.get('state')

    return BookingBase().modify_booking(booking_id, request.user.id, state, note)
