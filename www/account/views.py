# -*- coding: utf-8 -*-

import urllib
import json
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from www.misc import qiniu_client
from www.misc.decorators import member_required
from www.account import interface

ub = interface.UserBase()


def home_welcome(request, template_name='pc/index.html'):
    # print request.META.get("HTTP_USER_AGENT")
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def car_list(request, template_name='pc/car_list.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def login(request, template_name='pc/account/login.html'):
    mobile = request.POST.get('mobile', '').strip()
    password = request.POST.get('password', '').strip()

    if request.POST:
        user = auth.authenticate(username=mobile, password=password)
        if user:
            auth.login(request, user)
            next_url = request.session.get('next_url') or '/'
            request.session.update(dict(next_url=''))
            return HttpResponseRedirect(next_url)
        else:
            warning_msg = u'用户名或者密码错误'
    else:
        # 从REUQEST中或者HTTP_REFERER中获取
        next_url = utils.get_next_url(request)
        if next_url:
            request.session['next_url'] = urllib.unquote_plus(next_url)

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def login_weixin(request, template_name='pc/account/login_weixin.html'):
    from www.weixin.interface import WeixinBase

    # 从REUQEST中或者HTTP_REFERER中获取
    next_url = utils.get_next_url(request)
    if next_url:
        request.session['next_url'] = urllib.unquote_plus(next_url)

    wb = WeixinBase()
    ticket_info = WeixinBase().get_qr_code_ticket(wb.init_app_key())
    if not ticket_info:
        raise Exception, u"获取微信登陆二维码异常"
    ticket = ticket_info["ticket"]
    expire = ticket_info["expire_seconds"]

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def regist(request, invitation_code=None, template_name='account/regist.html'):
    email = request.POST.get('email', '').strip()
    nick = request.POST.get('nick', '').strip()
    password = request.POST.get('password', '').strip()
    re_password = request.POST.get('re_password', '').strip()
    captcha = request.POST.get('captcha', '').strip()

    if request.POST:
        if captcha and request.session.get("captcha", "").strip() == captcha:
            errcode, result = ub.regist_user_with_transaction(email, nick, password, re_password, ip=utils.get_clientip(request),
                                                              invitation_code=request.session.get('invitation_code'))
            if errcode == 0:
                user = auth.authenticate(username=email, password=password)
                auth.login(request, user=user)
                next_url = request.session.get('next_url') or '/'
                request.session.update(dict(next_url='', invitation_code=''))
                return HttpResponseRedirect(next_url)
            else:
                warning_msg = result
        else:
            warning_msg = u"请输入正确的验证码"
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def captcha(request):
    from common.generate_captcha import create_validate_code
    code_img = create_validate_code()
    request.session["captcha"] = code_img[1]

    response = HttpResponse(mimetype="image/gif")
    response.__setitem__('Expires', '0')
    response.__setitem__('Pragma', 'no-cache')
    code_img[0].save(response, "GIF")
    return response


def forget_password(request, template_name='account/forget_password.html'):
    if request.POST:
        email = request.POST.get('email')
        errcode, result = ub.send_forget_password_email(email)
        if errcode != 0:
            error_msg = result
        else:
            success_msg = u'找回密码邮件已经发送，请登录邮箱后操作'

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def reset_password(request, template_name='account/reset_password.html'):
    if not request.POST:
        code = request.REQUEST.get('code')
        user = ub.get_user_by_code(code)
        if not user:
            error_msg = interface.dict_err.get(112)
            return render_to_response('account/forget_password.html', locals(), context_instance=RequestContext(request))
        else:
            request.session['reset_password_code'] = code
    else:
        new_password_1 = request.POST.get('new_password_1')
        new_password_2 = request.POST.get('new_password_2')
        code = request.session['reset_password_code']
        errcode, result = ub.reset_password_by_code(code, new_password_1, new_password_2)
        if errcode != 0:
            error_msg = result
        else:
            success_msg = u'密码修改成功，请重新登录'
            user = result
            user.backend = 'www.middleware.user_backend.AuthBackend'
            auth.login(request, user)
            request.session['reset_password_code'] = ''
            return HttpResponseRedirect('/')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def get_user_by_nick(request, nick):
    user = ub.get_user_by_nick(nick)
    if user:
        return HttpResponseRedirect(user.get_url())
    else:
        err_msg = u'用户不存在'
        return render_to_response('error.html', locals(), context_instance=RequestContext(request))


@member_required
def change_profile(request, template_name='account/change_profile.html'):
    img_key = 'avatar_%s' % utils.uuid_without_dash()   # 七牛上传图片文件名
    uptoken = qiniu_client.get_upload_token(img_key)    # 七牛图片上传token
    if request.POST:
        nick = request.POST.get('nick')
        gender = request.POST.get('gender', '').strip()
        birthday = request.POST.get('birthday', '').strip()
        des = request.POST.get('des', '').strip()

        errcode, result = ub.change_profile(request.user, nick, gender, birthday, des)
        if errcode != 0:
            error_msg = result
        else:
            success_msg = u'修改资料成功'
            request.user = result
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def change_pwd(request, template_name='account/change_pwd.html'):
    if request.POST:
        old_password = request.POST.get('old_password')
        new_password_1 = request.POST.get('new_password_1')
        new_password_2 = request.POST.get('new_password_2')

        errcode, result = ub.change_pwd(request.user, old_password, new_password_1, new_password_2)
        if errcode != 0:
            error_msg = result
        else:
            success_msg = u'密码修改成功'
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def change_email(request, template_name='account/change_email.html'):
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')

        errcode, result = ub.change_email(request.user, email, password)
        if errcode != 0:
            error_msg = result
        else:
            success_msg = u'邮箱修改成功'
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def verify_email(request, template_name='account/change_email.html'):
    code = request.GET.get('code')

    if not code:
        ub.send_confirm_email(request.user)
        success_msg = u'验证邮件发送成功，请登陆邮箱操作'
    else:
        errcode, result = ub.check_email_confim_code(request.user, code)
        if errcode == 0:
            request.user = result
            success_msg = u'邮箱验证成功'
        else:
            error_msg = result
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@member_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


@member_required
def user_journey(request, user_id, template_name="account/user_journey.html"):
    from www.journey.interface import JourneyBase

    user = ub.get_user_by_id(user_id)
    if not user:
        raise Http404
    is_me = request.user == user

    jb = JourneyBase()
    journeys = jb.get_journeys_by_user_id(user_id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(journeys, count=10, page=page_num).info
    journeys = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    journeys = jb.format_journeys(journeys)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def user_answer(request, user_id, template_name="account/user_answer.html"):
    from www.answer.interface import AnswerBase

    user = ub.get_user_by_id(user_id)
    if not user:
        raise Http404
    is_me = request.user == user

    ab = AnswerBase()
    answers = ab.get_user_sended_answer(user_id)

    # 分页
    page_num = int(request.REQUEST.get('page', 1))
    page_objs = page.Cpt(answers, count=10, page=page_num).info
    answers = page_objs[0]
    page_params = (page_objs[1], page_objs[4])

    answers = ab.format_answers(answers, need_obj=True)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

# ===================================================ajax部分=================================================================#


@member_required
def get_user_info_by_id(request):
    '''
    @note: 根据用户id获取名片信息
    '''
    user_id = request.REQUEST.get('user_id')
    infos = {}
    if user_id:
        user = ub.get_user_by_id(user_id)
        if user:
            infos = dict(user_id=user.id, nick=user.nick, avatar=user.get_avatar_65(), des=(user.des or '').strip(), gender=user.gender)

            user_count_info = interface.UserCountBase().get_user_count_info(user_id)
            user_question_count, user_answer_count, user_liked_count = user_count_info['user_question_count'], \
                user_count_info['user_answer_count'], user_count_info['user_liked_count']
            infos.update(dict(user_question_count=user_question_count, user_answer_count=user_answer_count, user_liked_count=user_liked_count))

    return HttpResponse(json.dumps(infos), mimetype='application/json')


@member_required
def get_user_info_by_nick(request):
    '''
    @note: 根据用户昵称获取名片信息
    '''
    user_nick = request.REQUEST.get('user_nick', '').strip()
    infos = ''
    if user_nick:
        user = ub.get_user_by_nick(user_nick)
        if user:
            infos = dict(user_id=user.id, nick=user.nick, avatar=user.get_avatar_65(), des=user.des or '', gender=user.gender)

    return HttpResponse(json.dumps(infos), mimetype='application/json')


def get_weixin_login_state(request):
    '''
    @note: 微信扫码登陆
    '''
    from common import cache

    ticket = request.REQUEST.get('ticket', '').strip()
    cache_obj = cache.Cache()
    key = u'weixin_login_state_%s' % ticket
    datas = cache_obj.get(key)

    if datas:
        errcode, errmsg, user_id = datas
    else:
        errcode, errmsg, user_id = -2, u"等待登陆中", ""
    next_url = ""

    if errcode == 0:
        user = ub.get_user_by_id(user_id)
        user.backend = 'www.middleware.user_backend.AuthBackend'
        auth.login(request, user)

        next_url = request.session.get('next_url') or '/'
        if user.is_staff() and next_url.startswith("/company"):  # 系统管理员登陆后跳转到管理平台
            next_url = "/admin"
        request.session.update(dict(next_url=''))
        # cache_obj.delete(key)

    return HttpResponse(json.dumps(dict(errcode=errcode, errmsg=errmsg, next_url=next_url)), mimetype='application/json')
