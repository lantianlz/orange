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

from common.utils import send_email

from www.company.interface import OrderBase


def undone_orders_notice():
    undone_orders = []
    for x in OrderBase().get_undone_orders_before_yesterdey():
        undone_orders.append(u"%s 于 %s 创建的订单未结" % (x.company.combine_name(), x.create_time.strftime('%Y-%m-%d %H:%M:%S')))

    if undone_orders:
        content = u"，\n".join(undone_orders)
        send_email('web@3-10.cc', u'共「%s」单订单未结：' % len(undone_orders), content)

        from www.weixin.interface import WeixinBase
        from www.account.interface import ExternalTokenBase
        

        persons = []
        persons.append('541798fc416311e5a8ba00163e001bb1') # 李聪
        persons.append('de918ec6dfb911e5bb1d00163e001bb1') # 刘磊
        persons.append('6ceca02e07ac11e69a9800163e001bb1') # 何翔
        persons.append('cbd396fc589111e6bd8200163e001bb1') # 任吉尧

        for person in persons:
            to_user_openid = ExternalTokenBase().get_weixin_openid_by_user_id(person)

            WeixinBase().send_todo_list_template_msg(
                to_user_openid, 
                u'瓜娃子，单子又没结完', 
                u'结束当日订单', 
                u'高', 
                u"搞紧哈，下次莫忘咯"
            )

if __name__ == '__main__':
    undone_orders_notice()
