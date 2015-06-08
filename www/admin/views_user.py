# -*- coding: utf-8 -*-

import json
import urllib
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required

from www.account.interface import UserBase, UserCountBase


@verify_permission('')
def user(request, template_name='pc/admin/user.html'):
    from www.account.models import User
    states = [{'name': x[1], 'value': x[0]} for x in User.state_choices]

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('query_user')
def search(request):
    user_nick = request.REQUEST.get('user_nick')
    page_index = int(request.REQUEST.get('page_index', 1))
    email = request.REQUEST.get('email')

    users = []
    ub = UserBase()
    users = ub.get_user_for_admin(user_nick, email)

    page_objs = page.Cpt(users, count=10, page=page_index).info

    # 格式化
    format_users = [ub.format_user_full_info(x.id if not isinstance(x.id, long) else x.user_id) for x in page_objs[0]]

    data = []
    num = 10 * (page_index - 1) + 0

    for user in format_users:

        num += 1
        data.append({
            'num': num,
            'user_id': user.id,
            'user_avatar': user.get_avatar_65(),
            'user_nick': user.nick,
            'user_des': user.des,
            'user_email': user.email,
            'is_admin': user.is_admin,
            'last_active': str(user.last_active),
            'register_date': str(user.create_time),
            'state': user.state,
            'source': user.source_display,
            'ip': user.ip
        })

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_user')
def get_user_by_id(request):
    user_id = request.REQUEST.get('user_id')
    data = ''

    user = UserBase().get_user_by_id(user_id)
    if user:
        user = UserBase().format_user_full_info(user.id)

        data = {
            'user_id': user.id,
            'user_avatar': user.get_avatar_25(),
            'user_avatar_300': user.get_avatar_300(),
            'user_nick': user.nick,
            'user_des': user.des,
            'user_email': user.email,
            'user_gender': user.gender,
            'birthday': str(user.birthday),
            'is_admin': user.is_admin,
            'last_active': str(user.last_active),
            'state': user.state,
            'source': user.source_display,
            'ip': user.ip,
            'register_date': str(user.create_time)
        }

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('modify_user')
@common_ajax_response
def modify_user(request):

    user_id = request.REQUEST.get('user_id')
    nick = request.REQUEST.get('nick')
    gender = request.REQUEST.get('gender')
    birthday = request.REQUEST.get('birthday')
    des = request.REQUEST.get('des')
    state = int(request.REQUEST.get('state'))

    user = UserBase().get_user_by_id(user_id)

    return UserBase().change_profile(user, nick, gender, birthday, des, state)

@verify_permission('add_user')
@common_ajax_response
def add_user(request):
    email = request.POST.get('email', '').strip()
    nick = request.POST.get('nick', '').strip()
    password = request.POST.get('password', '').strip()
    re_password = request.POST.get('re_password', '').strip()
    ip = utils.get_clientip(request)

    flag, msg = UserBase().regist_user(email, nick, password, re_password, ip)
    return flag, msg.id if flag == 0 else msg

@member_required
def get_user_by_nick(request):
    '''
    根据名字查询用户
    '''
    nick = request.REQUEST.get('nick')

    result = []

    user = UserBase().get_user_by_nick(nick)

    if user:
        result.append([user.id, user.nick, None, user.nick])

    return HttpResponse(json.dumps(result), mimetype='application/json')

@verify_permission('change_pwd')
@common_ajax_response
def change_pwd(request):

    user_id = request.REQUEST.get('user_id')
    pwd = request.REQUEST.get('pwd')

    return UserBase().change_pwd_by_admin(user_id, pwd)