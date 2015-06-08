# -*- coding: utf-8 -*-

import time
import datetime

# from pprint import pprint
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils
from www.misc.oauth2 import format_external_user_info
from www.account.interface import UserBase


def oauth_qq(request):
    from www.misc.oauth2.qq import Consumer
    client = Consumer()

    code = request.REQUEST.get('code')
    if not code:
        return HttpResponseRedirect(client.authorize())
    else:
        # 获取access_token
        dict_result = client.token(code)
        access_token = dict_result.get('access_token')

        # 获取用户信息
        openid = client.get_openid(access_token)
        user_info = client.request_api(access_token, '/user/get_user_info', data=dict(access_token=access_token, openid=openid))
        user_info = format_external_user_info(user_info, 'qq')
        flag, result = UserBase().get_user_by_external_info(source='qq', access_token=access_token, external_user_id=openid,
                                                            refresh_token=dict_result['refresh_token'], nick=user_info['nick'],
                                                            ip=utils.get_clientip(request), expire_time=dict_result['expires_in'],
                                                            user_url=user_info['url'], gender=user_info['gender'])
        if flag:
            user = result
            user.backend = 'www.middleware.user_backend.AuthBackend'
            auth.login(request, user)
            next_url = request.session.get('next_url') or '/'
            request.session.update(dict(next_url=''))
            return HttpResponseRedirect(next_url)
        else:
            error_msg = result or u'qq账号登陆失败，请重试'
            return render_to_response('account/login.html', locals(), context_instance=RequestContext(request))

        return HttpResponse(u'code is %s' % code)


def oauth_sina(request):
    from www.misc.oauth2.sina import Consumer
    client = Consumer()

    code = request.REQUEST.get('code')
    if not code:
        return HttpResponseRedirect(client.authorize())
    else:
        # 获取access_token
        dict_result = client.token(code)
        access_token = dict_result.get('access_token')

        # 获取用户信息
        openid = dict_result['uid']
        user_info = client.request_api(access_token, '/2/users/show.json', data=dict(access_token=access_token, uid=openid))
        # pprint(user_info)
        user_info = format_external_user_info(user_info, 'sina')

        flag, result = UserBase().get_user_by_external_info(source='sina', access_token=access_token, external_user_id=openid,
                                                            refresh_token=dict_result['refresh_token'], nick=user_info['nick'],
                                                            ip=utils.get_clientip(request), expire_time=dict_result['expires_in'],
                                                            user_url=user_info['url'], gender=user_info['gender'])
        if flag:
            user = result
            user.backend = 'www.middleware.user_backend.AuthBackend'
            auth.login(request, user)
            next_url = request.session.get('next_url') or '/'
            request.session.update(dict(next_url=''))
            return HttpResponseRedirect(next_url)
        else:
            error_msg = result or u'新浪微博账号登陆失败，请重试'
            return render_to_response('account/login.html', locals(), context_instance=RequestContext(request))

        return HttpResponse(u'code is %s' % code)


def oauth_weixin(request):
    import logging
    from www.misc.oauth2.weixin import Consumer
    from www.weixin.interface import dict_weixin_app, WexinBase
    from www.tasks import async_change_profile_from_weixin

    app_key = WexinBase().init_app_key()
    client = Consumer(app_key)

    code = request.REQUEST.get('code')
    if not code:
        return HttpResponseRedirect(client.authorize())
    else:
        weixin_state = request.GET.get("state")

        # 获取access_token
        dict_result = client.token(code)
        access_token = dict_result.get('access_token')
        # logging.error(dict_result)

        # dict_result={u'errcode': 40029, u'errmsg': u'invalid code'}
        if dict_result.get("errcode") == 40029:  # 重新授权
            return HttpResponseRedirect(client.authorize())

        # 自动检测用户登陆
        openid = dict_result.get("openid")
        user_info = dict(nick=u"weixin_%s" % int(time.time() * 1000), url="", gender=0)

        flag, result = UserBase().get_user_by_external_info(source='weixin', access_token=access_token, external_user_id=openid,
                                                            refresh_token=None, nick=user_info['nick'],
                                                            ip=utils.get_clientip(request), expire_time=dict_result['expires_in'],
                                                            user_url=user_info['url'], gender=user_info['gender'], app_id=dict_weixin_app[app_key]["app_id"])
        if flag:
            user = result
            user.backend = 'www.middleware.user_backend.AuthBackend'
            auth.login(request, user)
            UserBase().update_user_last_login_time(user.id, ip=utils.get_clientip(request), last_active_source=2)

            # 更新用户资料
            if settings.LOCAL_FLAG:
                async_change_profile_from_weixin(user, app_key, openid)
            else:
                async_change_profile_from_weixin.delay(user, app_key, openid)

            dict_next = {"home": "/car_wash/", "order_code": "/car_wash/order_code",  "recharge": "/cash/recharge",
                         "coupon": "/car_wash/coupon", "about": "/s/about", "help": "/s/help", "shop": "/shop/"}
            next_url = dict_next.get(weixin_state, "/car_wash/")

            return HttpResponseRedirect(next_url)
        else:
            error_msg = result or u'微信登陆失败，请重试'
            return HttpResponse(error_msg)

        return HttpResponse(u'code is %s' % (code, ))
