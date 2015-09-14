# -*- coding: utf-8 -*-

import urllib
import re
import json
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required
from www.weixin.interface import WeixinBase, Sign

@verify_permission('')
def home(request):
    return HttpResponseRedirect('/admin/user')

@member_required
@verify_permission('')
def nav(request):
    # 微信key
    url = 'http://www.3-10.cc/admin/nav'
    sign = Sign(WeixinBase().get_weixin_jsapi_ticket(WeixinBase().init_app_key()), url)
    sign_dict = sign.sign()

    return render_to_response('pc/admin/nav.html', locals(), context_instance=RequestContext(request))