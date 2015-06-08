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


import commands
import time
import re
from common.utils import send_email
from django.conf import settings


def main(limit):
    """
    /usr/bin/tail -n 500000 /var/log/nginx/www.log | grep 61.140.150.163 | awk -F"HTTP" {'print $1'} | awk -F"\"" {'print $2'}| sort |uniq -c |sort -rn |awk '{ if($1>1) print count $1 " url "$2" "$3}'
    """
    t1 = time.time()
    cmd_www = """/usr/bin/tail -n 500000 /var/log/nginx/www.log | grep -v 127.0.0.1 | awk -F"-" {'print $1'} | sort |uniq -c |sort -rn |awk '{ if($1>%s) print "count " $1 " ip "$2 }' """ % limit

    content_www = commands.getoutput(cmd_www)

    t2 = time.time()
    content = u'www.log info is:\n%s \n\n' % (content_www,)
    time_content = u'shell run time:%.1f second' % (t2 - t1, )
    if check_content(content_www):
        file_name = '%s/../scripts/crontab/last_analyze_log.txt' % settings.SITE_ROOT
        try:
            f = open(file_name, 'r')
            file_content = f.read()
            f.close()
        except:
            file_content = ''

        if content != file_content:
            send_email(emails=settings.NOTIFICATION_EMAIL,
                       title=u'frequent ip of nginx log from %s' % settings.SERVER_NAME,
                       content=content + time_content, type="text")
            f = open(file_name, 'w')
            f.write(content)
            f.close()

    print 'ok'


def check_content(content):
    exclude_set = set(['', ])

    p = re.compile(u'ip (\d+.\d+.\d+.\d+)', re.I)
    print set(p.findall(content)) - exclude_set
    if set(p.findall(content)) - exclude_set:
        return True


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        limit = 1000
    else:
        limit = int(sys.argv[1])
    main(limit)
