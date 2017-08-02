# -*- coding: utf-8 -*-

import json
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.company.interface import ParttimeRecordBase, ParttimePersonBase


@verify_permission('')
def parttime_record(request, template_name='pc/admin/parttime_record.html'):
    from www.company.models import ParttimeRecord

    dates = utils.get_range_date_of_week()
    start_date = dates[0]
    end_date = dates[6]

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_record(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'record_id': x.id,
            'person_id': x.person.id,
            'person_name': x.person.name,
            'start_time': str(x.start_time),
            'end_time': str(x.end_time),
            'hour': x.hour,
            'hourly_pay': x.hourly_pay,
            'pay': x.pay,
            'note': x.note,
            'create_time': str(x.create_time)
        })

    return data


@verify_permission('query_parttime_record')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    page_index = int(request.REQUEST.get('page_index'))

    objs, sum_price = ParttimeRecordBase().search_records_for_admin(start_date, end_date, name)

    page_objs = page.Cpt(objs, count=20, page=page_index).info

    # 格式化json
    num = 20 * (page_index - 1)
    data = format_record(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5], 'sum_price': sum_price or 0}),
        mimetype='application/json'
    )


@verify_permission('add_parttime_record')
@common_ajax_response
def add_record(request):
    '''
    '''
    person_id = request.REQUEST.get('person_id')
    start_date = request.REQUEST.get('start_date')
    end_date = request.REQUEST.get('end_date')
    note = request.REQUEST.get('note')

    flag, msg = ParttimeRecordBase().add_record(
        person_id, start_date, end_date, note
    )

    return flag, msg.id if flag == 0 else msg


@verify_permission('remove_parttime_record')
@common_ajax_response
def remove_record(request):
    '''
    '''
    record_id = request.REQUEST.get('record_id')

    return ParttimeRecordBase().remove_record(record_id)


@verify_permission('add_parttime_record')
def file_import(request):
    parttime_record_file = request.FILES.get('parttime_record_file')

    if parttime_record_file:
        import tempfile
        temp_file = tempfile.NamedTemporaryFile()

        try:
            temp_file.write(parttime_record_file.read())
            temp_file.flush()

            data = utils.get_excel_data(temp_file.name, 3)
            # dates = utils.get_range_date_of_week()

            for x in data:
                # 首先判断日期
                # if x[3] not in dates:
                #     continue

                # 是否两次打卡
                if not (x[4] and x[5]):
                    continue
                # 是否有此兼职
                person = ParttimePersonBase().get_person_by_name(x[1])
                if not person:
                    continue

                ParttimeRecordBase().add_record(
                    person.id,
                    '%s %s' % (x[3], x[4]),
                    '%s %s' % (x[3], x[5]),
                    u'批量导入'
                )
        except Exception, e:
            print e

        finally:
            temp_file.close()

    return HttpResponseRedirect("/admin/parttime_record")
