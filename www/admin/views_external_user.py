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

from www.account.interface import UserBase, ExternalTokenBase


@verify_permission('')
def external(request, template_name='pc/admin/external_user.html'):
    from www.account.models import ExternalToken
    source_choices = [{'value': x[0], 'name': x[1]} for x in ExternalToken.source_choices]
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('query_external')
def get_external(request):
    page_index = int(request.REQUEST.get('page_index', 1))

    s_date = request.REQUEST.get('s_date')
    s_date = (s_date if s_date else datetime.datetime.now().strftime('%Y-%m-%d')) + " 00:00:00"

    e_date = request.REQUEST.get('e_date')
    e_date = (e_date if e_date else datetime.datetime.now().strftime('%Y-%m-%d')) + " 23:59:59"

    nick = request.REQUEST.get('nick')

    objs = ExternalTokenBase().get_external_for_admin(s_date, e_date, nick)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    data = []
    num = 10 * (page_index - 1) + 0

    for x in page_objs[0]:

        num += 1

        user = UserBase().get_user_by_id(x.user_id) if x.user_id else None

        data.append({
            'num': num,
            'external_id': x.id,
            'user_id': x.user_id if user else '',
            'user_nick': x.nick if user else '',
            'source': x.source,
            'access_token': x.access_token,
            'refresh_token': x.refresh_token,
            'external_user_id': x.external_user_id,
            'union_id': x.union_id,
            'app_id': x.app_id,
            'nick': x.nick,
            'user_url': x.user_url,
            'expire_time': str(x.expire_time),
            'create_time': str(x.create_time),
            'update_time': str(x.update_time),
            'state': x.state
        })

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )
