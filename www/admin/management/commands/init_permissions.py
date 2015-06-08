# -*- coding: utf-8 -*-

import json
from django.core.management.base import BaseCommand
from optparse import make_option

from misc import consts

from admin.models import Permission
from admin.interface import PermissionBase
from www.account.interface import UserBase


class Command(BaseCommand):

    help = u'初始化权限数据，并可以添加管理员 eg: python manage.py init_permissions [-u a@q.com]'

    option_list = BaseCommand.option_list + (
        make_option('-u',
                    '--user',
                    action='store',
                    dest='user',
                    default='',
                    help=u'添加管理员, 输入邮箱'),
    )

    def handle(self, *args, **options):
        print u'==================初始化权限数据开始...'

        cache = {}

        for p in consts.PERMISSIONS:

            obj, created = Permission.objects.get_or_create(name=p['name'], code=p['code'])

            cache[obj.code] = obj.id

            # 设置父节点
            if p['parent']:
                obj.parent_id = cache[p['parent']]
                obj.save()

        print u'==================初始化权限数据完成'
        print

        email = options.get('user')
        if email:
            print u'==================设置[%s]为管理员...' % email
            user = UserBase().get_user_by_email(email)
            if not user:
                print u'==================没有该用户，设置管理员失败...'
            else:
                permissions = [x.id for x in Permission.objects.all()]
                code, msg = PermissionBase().save_user_permission(user.id, permissions, user.id)
                if code == 0:
                    print u'==================添加管理员成功'
                else:
                    print u'==================%s, 设置管理员失败...' % msg
