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


import datetime
from django.conf import settings
from www.company.interface import InvoiceRecordBase


def get_invoice_statement():
    data, total = InvoiceRecordBase().get_invoice_statement('', '2015-08-21', datetime.datetime.now())
    companys = []

    # 找出所有充值金额不匹配
    for x in filter(lambda x: x['offset'] < 0, data):
        companys.append(u"%s欠费 %s 元" % (x['combine_name'], x['offset_abs']))

    if companys:
        InvoiceRecordBase().send_invoice_notice(u"，\n".join(companys))

if __name__ == "__main__":
    get_invoice_statement()
