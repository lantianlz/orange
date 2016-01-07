# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.account.interface import UserBase
from www.company.interface import InventoryRecordBase

@verify_permission('')
def inventory_record(request, template_name='pc/admin/inventory_record.html'):
    from www.company.models import InventoryRecord

    operation_choices = [{'value': x[0], 'name': x[1]} for x in InventoryRecord.operation_choices]
    all_operations = [{'value': x[0], 'name': x[1]} for x in InventoryRecord.operation_choices]
    all_operations.append({'value': -1, 'name': u"全部"})
    
    today = datetime.datetime.now()
    start_date= (today.replace(day=1)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_record(objs, num):
    data = []

    for x in objs:
        num += 1

        user = UserBase().get_user_by_id(x.operator) if x.operator else ''

        data.append({
            'num': num,
            'recore_id': x.id,
            'inventory_id': x.inventory.id,
            'inventory_name': x.inventory.item.name,
            'operation': x.operation,
            'operation_str': x.get_operation_display(),
            'notes': x.notes,
            'value': x.value,
            'current_value': x.current_value,
            'user_id': user.id if user else '',
            'user_nick': user.nick if user else '',
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_inventory_record')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    operation = request.REQUEST.get('operation', '-1')
    operation = None if operation == "-1" else int(operation)
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    page_index = int(request.REQUEST.get('page_index'))

    objs = InventoryRecordBase().search_records_for_admin(start_date, end_date, name, operation)

    page_objs = page.Cpt(objs, count=20, page=page_index).info

    # 格式化json
    num = 20 * (page_index - 1)
    data = format_record(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('add_inventory_record')
@common_ajax_response
def add_record(request):
    '''
    '''
    inventory_id = request.REQUEST.get('inventory')
    operation = request.REQUEST.get('operation')
    value = request.REQUEST.get('value')
    notes = request.REQUEST.get('notes')

    flag, msg = InventoryRecordBase().add_record_with_transaction(
        inventory_id, operation, value, request.user.id, notes
    )

    return flag, msg.id if flag == 0 else msg







