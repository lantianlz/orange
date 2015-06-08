# -*- coding: utf-8 -*-

import sys
import os

# 引入父目录来引入其他模块
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


import time
import json
import requests
import datetime
from pyquery import PyQuery as pq
from django.conf import settings
from www.car.models import Brand, Serial, CarBasicInfo

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0"}


def get_car():

    url = "http://pg.taoche.com/ajax/carinfojs.ashx?_=%s" % int(time.time() * 1000)
    text = requests.get(url, timeout=30, headers=headers).text
    # print text.encode("utf8")

    text = text.split('"')[1]
    cs = text.split(",")
    for i, c in enumerate(cs):

        if i % 2 == 0:
            first_word, name = c.strip().split(" ", 1)
            ex_id = cs[i + 1].strip()
            print first_word, name.encode("utf8"), ex_id
            if not Brand.objects.filter(name=name):
                Brand.objects.create(name=name, first_word=first_word, ex_id=ex_id)


if __name__ == '__main__':
    get_car()
