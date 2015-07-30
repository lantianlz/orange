# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required

from www.company.interface import ItemBase

@verify_permission('')
def item(request, template_name='pc/admin/item.html'):
    from www.company.models import Item
    states = [{'name': x[1], 'value': x[0]} for x in Item.state_choices]
    types = [{'name': x[1], 'value': x[0]} for x in Item.type_choices]
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_item(objs, num):
    data = []

    for x in objs:
        num += 1

        data.append({
            'num': num,
            'item_id': x.id,
            'name': x.name,
            'price': str(x.price),
            'item_type': x.item_type,
            'spec': x.spec,
            'state': x.state,
            'code': x.code,
            'img': x.img
        })

    return data


@verify_permission('query_user')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    page_index = int(request.REQUEST.get('page_index'))

    objs = ItemBase().search_items_for_admin(name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_item(page_objs[0], num)

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

@verify_permission('add_item')
@common_ajax_response
def add_item(request):
    name = request.POST.get('name')
    item_type = request.POST.get('item_type')
    spec = request.POST.get('spec')
    price = request.POST.get('price')
    sort = request.POST.get('sort')

    flag, msg = ItemBase().add_item(name, item_type, spec, price, sort)
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