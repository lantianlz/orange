# -*- coding: utf-8 -*-
"""
@note: 分析ngxin日志，提取出频繁访问网站的ip
"""

import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


from common import cache
from common.utils import send_email
from django.conf import settings


WORKER_CONFIG = [
    {
        'name': 'www_worker',
        'limit': 100,
    },
    {
        'name': 'email_worker',
        'limit': 200,
    },
]


def get_delay_count(key):
    cache_obj = cache.Cache(cache.CACHE_WORKER)
    return cache_obj.llen(key)


def main():
    warn_list = []
    for item in WORKER_CONFIG:
        count = get_delay_count(item['name'])
        print u'---%s----%s----' % (item['name'], count)
        if count > item.get('limit'):
            item['count'] = count
            warn_list.append(item)
    if warn_list:
        title = u'%s主机 worker积压警告' % (settings.SERVER_NAME, )
        content = u''
        for item in warn_list:
            content += u'%(name)s:积压任务数%(count)s， 警戒值为%(limit)s\n' % item

        send_email(emails=settings.NOTIFICATION_EMAIL, title=title, content=content, type="text")

    print 'ok'


if __name__ == '__main__':
    main()
