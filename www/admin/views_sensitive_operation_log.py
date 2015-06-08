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
from www.custom_tags.templatetags.custom_filters import str_display

from www.admin.interface import SensitiveOperationLogBase
from www.account.interface import UserBase

@verify_permission('')
def sensitive_operation_log(request, template_name='pc/admin/sensitive_operation_log.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('query_sensitive_operation_log')
def get_sensitive_operation_log(request):

    nick = request.REQUEST.get('nick')
    page_index = int(request.REQUEST.get('page_index', 1))

    objs = SensitiveOperationLogBase().search_logs_for_admin(nick)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    data = []
    num = 10 * (page_index - 1) + 0

    for log in page_objs[0]:

        num += 1

        user = UserBase().get_user_by_id(log.user_id)

        data.append({
            'num': num,
            'user_id': user.id,
            'user_nick': user.nick,
            'url': log.url,
            'create_date': str(log.create_time),
            'data': log.data
        })

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )