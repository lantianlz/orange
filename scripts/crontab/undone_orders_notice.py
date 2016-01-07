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

if __name__ == '__main__':
    undone_orders_notice()
