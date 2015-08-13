# -*- coding: utf-8 -*-

import json
import time

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from misc.decorators import common_ajax_response, member_required
from www.company.interface import BookingBase
from www.account.interface import UserBase
from www.weixin.interface import WeixinBase, Sign


def booking(request, template_name='mobile/booking.html'):

    invite_by = request.REQUEST.get('invite_by')
    if invite_by:
        invite = UserBase().get_user_by_id(invite_by)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@common_ajax_response
def get_booking(request):

    company_name = request.REQUEST.get('company')
    staff_name = request.REQUEST.get('name')
    mobile = request.REQUEST.get('mobile')
    source = request.REQUEST.get('source')
    invite_by = request.REQUEST.get('invite_by')

    return BookingBase().add_booking(company_name, staff_name, mobile, source, invite_by)


@member_required
def invite(request, template_name='mobile/invite.html'):

    # 微信key
    url = 'http://www.3-10.cc/company/invite'
    sign = Sign(WeixinBase().get_weixin_jsapi_ticket(WeixinBase().init_app_key()), url)
    sign_dict = sign.sign()

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))
