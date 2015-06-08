# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission, log_sensitive_operation
from www.misc import qiniu_client
from common import utils, page

from www.account.interface import UserBase
from www.cash.interface import UserCashRecordBase

@verify_permission('')
def user_cash_record(request, template_name='pc/admin/user_cash_record.html'):
    from www.cash.models import operation_choices
    operation_choices = [{'value': x[0], 'name': x[1]} for x in operation_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_record(objs, num):
    data = []

    for x in objs:
        num += 1

        user = UserBase().get_user_by_id(x.user_cash.user_id)

        data.append({
            'num': num,
            'record_id': x.id,
            'user_id': user.id,
            'user_nick': user.nick,
            'user_email': user.email,
            'balance': str(x.user_cash.balance),
            'value': str(x.value),
            'current_balance': str(x.current_balance),
            'operation': x.operation,
            'notes': x.notes,
            'ip': x.ip,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_user_cash_record')
def search(request):
    data = []

    nick = request.REQUEST.get('nick')

    page_index = int(request.REQUEST.get('page_index'))

    objs = UserCashRecordBase().search_records_for_admin(nick)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_record(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )

@verify_permission('add_user_cash_record')
@log_sensitive_operation
@common_ajax_response
def add_record(request):
    user_id = request.REQUEST.get('user_id')
    value = request.REQUEST.get('value')
    operation = request.REQUEST.get('operation')
    notes = request.REQUEST.get('notes')

    return UserCashRecordBase().add_record_with_transaction(user_id, value, operation, notes)