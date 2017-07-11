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
from www.weixin.interface import WeixinBase
from www.account.interface import ExternalTokenBase

def confirm_tomorrow_order():

    persons = []
    persons.append('074618b2419211e5ae3000163e001bb1') # 曹艳珺
    persons.append('fba5a110794211e5948e00163e001bb1') # 罗杰
    # persons.append('b88b7ec660fc11e5bf2700163e001bb1') # 肖仁凡

    for person in persons:
        to_user_openid = ExternalTokenBase().get_weixin_openid_by_user_id(person)

        WeixinBase().send_todo_list_template_msg(
            to_user_openid, 
            u'亲们，早点和客户沟通明天的订单', 
            u'确认明天订单', 
            u'高', 
            u"搞紧哈，不要我紧到催！"
        )

if __name__ == '__main__':
    confirm_tomorrow_order()
