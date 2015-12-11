# -*- coding: utf-8 -*-

"""
@note: 和权限相关的装饰器添加
@author: lizheng
@date: 2013-12-10
"""


import urllib
import json
from functools import wraps
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import cache, utils


def member_required(func):
    """
    @note: 过滤器, 是否是会员
    @author: lizheng
    @date: 2013-12-10
    """
    def _decorator(request, *args, **kwargs):
        from www.misc.oauth2.weixin import Consumer
        from www.weixin.interface import WeixinBase

        if not (hasattr(request, 'user') and request.user.is_authenticated()):
            if request.is_ajax():
                return HttpResponse('need_login')
            else:
                user_agent = request.META.get("HTTP_USER_AGENT", "").lower()

                if "micromessenger" in user_agent:  # 微信端自动登录
                    return HttpResponseRedirect(Consumer(WeixinBase().init_app_key()).authorize())

                if "android" in user_agent or "iphone" in user_agent:   # 手机浏览器端需要处理
                    err_msg = u'需要登陆后进行操作<br /><br />请在微信中搜索公众号「三点十分」，关注后通过菜单访问'
                    return render_to_response('error.html', locals(), context_instance=RequestContext(request))

                # 电脑端跳转到登陆页面
                try:
                    url = urllib.quote_plus(request.get_full_path())
                except:
                    url = '/'
                return HttpResponseRedirect("/login_weixin?next_url=%s" % url)

        return func(request, *args, **kwargs)
    return _decorator


def staff_required(func):
    """
    @note: 过滤器, 是否是内部成员
    @author: lizheng
    @date: 2013-12-10
    """
    def _decorator(request, *args, **kwargs):
        if not (hasattr(request, 'user') and request.user.is_authenticated() and request.user.is_staff()):
            if request.is_ajax():
                return HttpResponse(u'need_staff')
            else:
                return HttpResponse(u'需要管理员权限才可')

        return func(request, *args, **kwargs)
    return _decorator


def protected_view(func):
    """
    @note: 过滤器, 站内的views，不对站外用户开发
    @author: lizheng
    @date: 2013-12-10
    """
    def _decorator(request, *args, **kwargs):
        authentication = request.REQUEST.get('authentication')
        if authentication != u'token':
            raise Exception, u'the request from mom authentication error!'
            return HttpResponse('it works, but authenticate error!')
        return func(request, *args, **kwargs)
    return _decorator


def cache_required(cache_key, cache_key_type=0, expire=3600 * 24, cache_config=cache.CACHE_TMP):
    '''
    @note: 缓存装饰器
    cache_key格式为1：'answer_summary_%s' 取方法的第一个值做键 2：'global_var'固定值
    如果需要格式化cache_key的话，cache_key_type为
    0：传参为：func(self, cache_key_param)
    1：传参为：func(cache_key_param)
    2：传参为：func(self) cache_key为self.id
    '''

    def _wrap_decorator(func):
        func.cache_key = cache_key

        def _decorator(*args, **kwargs):
            cache_key = func.cache_key
            must_update_cache = kwargs.get('must_update_cache')
            if '%' in cache_key:
                assert len(args) > 0
                if cache_key_type == 0:
                    key = args[1].id if hasattr(args[1], 'id') else args[1]
                    assert isinstance(key, (unicode, str, int, long, float))
                    cache_key = cache_key % key
                if cache_key_type == 1:
                    cache_key = cache_key % args[0]
                if cache_key_type == 2:
                    cache_key = cache_key % args[0].id
            return cache.get_or_update_data_from_cache(cache_key, expire, cache_config, must_update_cache, func, *args, **kwargs)
        return _decorator
    return _wrap_decorator


def common_ajax_response(func):
    """
    @note: 通用的ajax返回值格式化，格式为：dict(errcode=errcode, errmsg=errmsg)
    """
    def _decorator(request, *args, **kwargs):
        result = func(request, *args, **kwargs)
        if isinstance(result, HttpResponse):
            return result
        errcode, errmsg = result

        # 将对象转义
        errmsg = 'ok' if (errcode == 0 and not isinstance(errmsg, (list, int, bool, long, float, unicode, str, type(None)))) else errmsg
        r = dict(errcode=errcode, errmsg=errmsg)
        return HttpResponse(json.dumps(r), mimetype='application/json')
    return _decorator


def verify_permission(permission):
    '''
    权限验证装饰器

    @verify_permission('delete_user')
    def delete(request):
        pass

    '''
    def permission_decorator(func):

        @wraps(func)
        def wrapper(request, *args, **kwargs):
            from admin.interface import PermissionBase
            # 获取用户所有权限
            user_permissions = PermissionBase().get_user_permissions(request.user.id)
            # print user_permissions

            # 如果是空，说明不是管理员
            if user_permissions == []:
                # return HttpResponse(u'需要管理员权限')
                raise Http404

            # 如果没有对应的权限
            if permission and permission not in user_permissions:
                # ajax 请求
                if request.is_ajax():
                    return HttpResponse('permission_denied', mimetype='application/json')
                else:
                    return HttpResponse(u'需要管理员权限')
            else:
                return func(request, *args, **kwargs)
        return wrapper
    return permission_decorator


def auto_select_template(func):
    """
    @note: 过滤器, 自动判断模板选择
    """
    def _decorator(request, *args, **kwargs):
        template_name = kwargs.get("template_name")
        if template_name:
            dict_user_agent = utils.format_user_agent(request.META.get('HTTP_USER_AGENT'))
            if dict_user_agent['device_type'] in ('pc', 'pad'):
                ps = template_name.split("/")
                if ps.__len__() > 1:
                    ps[0] = "pc"
                template_name = "/".join(ps)

            if dict_user_agent['device_type'] in ('phone',):
                ps = template_name.split("/")
                if ps.__len__() > 1:
                    ps[0] = "mobile"
                template_name = "/".join(ps)

            kwargs.update(dict(template_name=template_name))
        return func(request, *args, **kwargs)
    return _decorator


def log_sensitive_operation(func):
    '''
    记录敏感操作流水
    '''
    def wrapper(request, *args, **kwargs):
        from admin.interface import SensitiveOperationLogBase

        SensitiveOperationLogBase().add_log(request.user.id, request.path, str(request.REQUEST))

        return func(request, *args, **kwargs)

    return wrapper


def company_manager_required_for_request(func):
    """
    @note: 过滤器, 公司平台使用
    """
    def _decorator(request, company_id, *args, **kwargs):
        from www.company.interface import CompanyBase, CompanyManagerBase

        company = CompanyBase().get_company_by_id(company_id)
        if not company:
            raise Http404

        is_cm = CompanyManagerBase().check_user_is_cm(company.id, request.user)
        if not is_cm:
            if request.is_ajax():
                return HttpResponse('{}')
            err_msg = u'权限不足，你还不是公司管理员，如有疑问请联系三点十分客服'
            return render_to_response('error.html', locals(), context_instance=RequestContext(request))

        request.company = company
        return func(request, company_id, *args, **kwargs)
    return _decorator


class request_limit_by_ip(object):

    """
    @note: 根据ip地址限制操作次数
    """

    def __init__(self, max_count, cycle=3600 * 24):
        self.max_count = max_count
        self.cycle = cycle

    def __call__(self, func):
        import datetime

        def _decorator(request, *args, **kwargs):
            cache_obj = cache.Cache()
            cache_key = u'%s_%s_%s' % (utils.get_function_code(func), utils.get_clientip(request),
                                       str(datetime.datetime.now().date()))
            cache_count = cache_obj.get(cache_key, original=True)
            if cache_count is None:
                cache_obj.set(cache_key, 1, time_out=self.cycle, original=True)
            else:
                cache_count = int(cache_count)
                cache_count += 1
                cache_obj.incr(cache_key)
                if cache_count > self.max_count:
                    if request.is_ajax():
                        # return 99900, "test"
                        return HttpResponse(json.dumps(dict(errcode=99900, errmsg=u'request limited by ip')), mimetype='application/json')
                    else:
                        return render_to_response('error.html', dict(err_msg=u'request limited by ip'),
                                                  context_instance=RequestContext(request))
            return func(request, *args, **kwargs)
        return _decorator
