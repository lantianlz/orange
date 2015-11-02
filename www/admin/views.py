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
# @verify_permission('')
def nav(request):

    # 用户角色判断，是否内部成员
    if request.user.is_staff():
        # 微信key
        url = 'http://www.3-10.cc/admin/nav'
        sign = Sign(WeixinBase().get_weixin_jsapi_ticket(WeixinBase().init_app_key()), url)
        sign_dict = sign.sign()
        return render_to_response('pc/admin/nav.html', locals(), context_instance=RequestContext(request))
    
    # 是否公司管理员
    else:
        from www.company.interface import CompanyManagerBase
        cm = CompanyManagerBase().get_cm_by_user_id(request.user.id)
        if cm:
            return HttpResponseRedirect("/company/%s/record" % cm.company.id)

        err_msg = u'权限不足，你还不是公司管理员，如有疑问请联系三点十分客服'
        return render_to_response('error.html', locals(), context_instance=RequestContext(request))
    