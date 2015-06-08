# -*- coding: utf-8 -*-

import logging
import hashlib
import time
from django.http import HttpResponse
from django.utils.encoding import smart_str

from www.weixin.interface import dict_weixin_app, WexinBase


def weixin_signature_required(func):
    """
    @note: 微信签名认证
    """
    def _decorator(request, *args, **kwargs):
        timestamp = request.GET.get('timestamp', '') or '0'
        nonce = request.GET.get('nonce', '')
        signature = request.GET.get('signature', '')
        token = dict_weixin_app[WexinBase().init_app_key()]['token']
        lst_sig = [timestamp, nonce, token]
        lst_sig.sort()
        if hashlib.sha1(''.join(lst_sig)).hexdigest() == signature and abs(int(time.time()) - int(timestamp)) < 3600:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse('<xml><error>signature error</error></xml>', mimetype='application/xml')
    return _decorator


# @weixin_signature_required
def index(request):
    logging.error('get info is:%s' % smart_str(request.GET))
    data = request.read()
    logging.error('post info is:%s' % smart_str(data))

    if data:
        xml = WexinBase().get_response(data) or '<xml></xml>'
        return HttpResponse(xml, mimetype='application/xml')
    else:
        return HttpResponse(request.REQUEST.get('echostr'))  # 修改微信配置url时和微信服务器鉴权
