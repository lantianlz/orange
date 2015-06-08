# -*- coding: utf-8 -*-

import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


user_id = 'f762a6f5d2b711e39a09685b35d0bf16'


def main():
    import time
    import datetime
    from django.conf import settings
    from common import utils
    from www.weixin.interface import WexinBase
    from www.tasks import async_send_email
    from pprint import pprint

    wb = WexinBase()
    app_key = "orange_test"
    to_user = 'oZy3hskE524Y2QbLgY2h3VnI3Im8'

    app_key = "orange"
    to_user = 'oNYsJj1eg4fnU4tKLvH-f2IXlxJ4'
    content = (u'古人云：鸟随鸾凤飞腾远，人伴贤良品质高。\n')

    # print wb.send_msg_to_weixin(content, to_user, app_key)

    context = {'reset_url': '%s/reset_password?code=%s' % (settings.MAIN_DOMAIN, "123"), }
    print async_send_email("web@3-10.club", u'来自三点十分', utils.render_email_template('email/reset_password.html', context), 'html')

    # pprint(wb.get_user_info(app_key, to_user))
    # pprint(wb.get_qr_code_ticket(app_key))
    # pprint(wb.send_buy_success_template_msg(to_user, name=u"三点十分行洗车码", remark=u"洗车码1: 0098 6543 1221   洗车码2: 7788 9954 1432", app_key=app_key))
    # pprint(wb.send_use_order_code_template_msg(to_user, product_type=u"消费项目", name=u"三点十分行", time=u"2013年8月20日 20:38",
    #                                            remark=u"洗车码「0280 1041 3114」已成功使用，欢迎再次购买", app_key=app_key))


if __name__ == '__main__':
    main()
