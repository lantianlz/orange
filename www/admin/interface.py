# -*- coding: utf-8 -*-

from django.db.models import Count
from django.db import transaction

from common import debug, cache
from www.misc import consts
from www.misc.decorators import cache_required

from www.admin.models import Permission, UserPermission, SensitiveOperationLog
from www.account.interface import UserBase

dict_err = {}

dict_err.update(consts.G_DICT_ERROR)


class PermissionBase(object):

    """docstring for PermissionBase"""

    def __init__(self):
        pass

    def get_all_permissions(self):
        '''
        获取所有权限
        '''
        return [x for x in Permission.objects.filter(parent__isnull=True)]

    def get_user_permissions(self, user_id):
        '''
        根据用户id 获取此用户所有权限
        '''
        return [x.permission.code for x in UserPermission.objects.filter(user_id=user_id)]

    def get_all_administrators(self):
        '''
        获取所有管理员
        '''
        user_ids = [x['user_id'] for x in UserPermission.objects.values('user_id').annotate(dcount=Count('user_id'))]

        return [UserBase().get_user_by_id(x) for x in user_ids]

    @transaction.commit_manually
    def save_user_permission(self, user_id, permissions, creator):
        '''
        修改用户权限
        '''

        if not user_id or not permissions or not creator:
            return 99800, dict_err.get(99800)

        try:
            UserPermission.objects.filter(user_id=user_id).delete()

            for x in permissions:
                UserPermission.objects.create(user_id=user_id, permission_id=x, creator=creator)

            transaction.commit()
        except Exception, e:
            print e
            transaction.rollback()
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def cancel_admin(self, user_id):
        '''
        取消管理员
        '''

        if not user_id:
            return 99800, dict_err.get(99800)

        UserPermission.objects.filter(user_id=user_id).delete()

        return 0, dict_err.get(0)


class FriendlyLinkBase(object):

    def __init__(self):
        pass

    def format_friendly_links(self, friendly_links):
        return friendly_links

    def add_friendly_link(self, name, href, link_type=0, des=None, sort_num=0):
        try:
            try:
                assert name and href

            except:
                return 99800, dict_err.get(99800)
            obj = FriendlyLink.objects.create(name=name, href=href, link_type=link_type, sort_num=sort_num, des=des)

            # 更新缓存
            self.get_all_friendly_link(must_update_cache=True)
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)
        return 0, obj.id

    @cache_required(cache_key='all_friendly_link_qx', expire=0, cache_config=cache.CACHE_STATIC)
    def get_all_friendly_link(self, state=True, must_update_cache=False):
        objects = FriendlyLink.objects.all()
        if state != None:
            objects = objects.filter(state=state)

        return objects

    def get_friendly_link_by_city_id(self, city_id, link_type=(0, )):
        flinks = []
        for flink in (self.get_all_friendly_link()):
            if flink.city_id == city_id and flink.link_type in link_type:
                flinks.append(flink)
        return flinks

    def get_friendly_link_by_id(self, link_id, state=True):
        return self.get_all_friendly_link(state).filter(id=link_id)

    def get_friendly_link_by_name(self, link_name):
        return self.get_all_friendly_link(state=None).filter(name=link_name)

    def get_friendly_link_by_link_type(self, link_type):
        flinks = []
        link_type = link_type if isinstance(link_type, (list, tuple)) else (link_type,)
        for flink in (self.get_all_friendly_link()):
            if flink.link_type in link_type:
                flinks.append(flink)
        return flinks

    def modify_friendly_link(self, link_id, **kwargs):
        if not link_id:
            return 99800, dict_err.get(99800)

        friendly_link = self.get_friendly_link_by_id(link_id, state=None)
        if not friendly_link:
            return 50103, dict_err.get(50103)

        friendly_link = friendly_link[0]

        try:
            for k, v in kwargs.items():
                setattr(friendly_link, k, v)

            friendly_link.save()

            # 更新缓存
            self.get_all_friendly_link(must_update_cache=True)
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def remove_friendly_link(self, link_id):
        if not link_id:
            return 99800, dict_err.get(99800)

        friendly_link = self.get_friendly_link_by_id(link_id, state=None)
        if not friendly_link:
            return 50103, dict_err.get(50103)
        friendly_link = friendly_link[0]
        friendly_link.delete()

        self.get_all_friendly_link(must_update_cache=True)
        return 0, dict_err.get(0)


class SensitiveOperationLogBase(object):

    def __init__(self):
        pass

    def add_log(self, user_id, url, data):
        SensitiveOperationLog.objects.create(user_id=user_id, url=url, data=data)

    def search_logs_for_admin(self, nick=''):

        objs = SensitiveOperationLog.objects.all()

        if nick:
            user = UserBase().get_user_by_nick(nick)

            if user:
                objs = objs.filter(user_id=user.id)
            else:
                objs = []
                
        return objs