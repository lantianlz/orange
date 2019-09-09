# -*- coding: utf-8 -*-

import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../www')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'

from www.weixin.interface import WeixinBase
from www.account.interface import ExternalTokenBase
from www.account.models import User, Profile


def buy_fruit_notice():

    persons = []

    for person in Profile.objects.filter(create_time__gte='2019-08-27 00:00:00'):
        to_user_openid = ExternalTokenBase().get_weixin_openid_by_user_id(person.id)

        WeixinBase().send_todo_list_template_msg(
            to_user_openid,
            u'多水果多VC，点击“员工团购”立刻下单水果，为您的健康保驾护航！',
            u'水果下单提醒',
            u'高',
            u"结束一天繁忙的工作，记得补充身体所需的营养哦～"
        )

if __name__ == '__main__':
    buy_fruit_notice()
