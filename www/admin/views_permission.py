# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from misc.decorators import staff_required, common_ajax_response, verify_permission
from common import utils, page

from www.admin.interface import PermissionBase
from www.account.interface import UserBase


@verify_permission('')
def permission(request, template_name='pc/admin/permission.html'):
    permissions = PermissionBase().get_all_permissions()
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('query_user_permission')
def get_all_administrators(request):
    '''
    获取所有管理员
    '''
    num = 0
    data = []

    for x in PermissionBase().get_all_administrators():
        num += 1
        data.append({
            'num': num,
            'user_id': x.id,
            'user_nick': x.nick,
            'user_avatar': x.get_avatar_65()
        })

    return HttpResponse(json.dumps(data), mimetype='application/json')


@verify_permission('query_user_permission')
def get_user_permissions(request):
    '''
    获取用户对应权限
    '''
    user_id = request.REQUEST.get('user_id')
    data = PermissionBase().get_user_permissions(user_id)
    user = UserBase().get_user_by_id(user_id)
    return HttpResponse(json.dumps({'permissions': data, 'user': {'user_id': user.id, 'user_nick': user.nick}}), mimetype='application/json')


@verify_permission('modify_user_permission')
@common_ajax_response
def save_user_permission(request):
    '''
    保存用户权限
    '''
    user_id = request.REQUEST.get('user_id')
    permissions = request.REQUEST.getlist('permissions')

    return PermissionBase().save_user_permission(user_id, permissions, request.user.id)


@verify_permission('cancel_admin')
@common_ajax_response
def cancel_admin(request):
    '''
    取消管理员
    '''
    user_id = request.REQUEST.get('user_id')

    return PermissionBase().cancel_admin(user_id)
