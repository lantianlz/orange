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


def get_brand():

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


def get_serial():
    for brand in Brand.objects.filter(parent_brand=None):
        url = "http://pg.taoche.com/ajax/carinfojs.ashx?carbrandid=%s&_=%s" % (brand.ex_id, int(time.time() * 1000))
        text = requests.get(url, timeout=30, headers=headers).text
        # print text.encode("utf8")

        cs = json.loads(text.split("=")[1])
        group_name_list = list(set([c["GroupName"] for c in cs]))

        for c in cs:
            group_name = c["GroupName"].strip()
            serial_name = c["Text"].strip()
            ex_id = c["Value"].strip()
            print group_name.encode("utf8"), serial_name.encode("utf8"), ex_id

            if len(group_name_list) == 1:
                serial_brand = brand
            else:
                if not Brand.objects.filter(parent_brand=brand, name=group_name):
                    serial_brand = Brand.objects.create(name=group_name, first_word=brand.first_word, parent_brand=brand, ex_id=0)
                else:
                    serial_brand = Brand.objects.get(parent_brand=brand, name=group_name)

            if not Serial.objects.filter(brand=serial_brand, name=serial_name):
                Serial.objects.create(brand=serial_brand, name=serial_name, ex_id=ex_id)


def get_car_basic_info():
    for serial in Serial.objects.all():
        url = "http://pg.taoche.com/ajax/carinfojs.ashx?carserialid=%s&_=%s" % (serial.ex_id, int(time.time() * 1000))
        text = requests.get(url, timeout=30, headers=headers).text
        print text.encode("utf8")

        cs = json.loads(text.split("=")[1])
        for c in cs:
            year = c["GroupName"].strip().split()[0]
            car_name = c["Text"].strip()
            ex_id = c["Value"].strip()
            print year.encode("utf8"), car_name.encode("utf8"), ex_id

            if not CarBasicInfo.objects.filter(name=car_name, serial=serial, year=year):
                CarBasicInfo.objects.create(name=car_name, year=year, ex_id=ex_id, serial=serial)


def get_car_original_price():
    for i, car in enumerate(CarBasicInfo.objects.select_related("serial").all().order_by("id")):
        if i < 16624:
            continue
        brand = car.serial.brand
        brand_ex_id = brand.ex_id or brand.parent_brand.ex_id
        current_year = datetime.datetime.now().year
        year = car.year if car.year != u"其他" else current_year
        if int(year) > current_year:
            year = current_year
        url = "http://www.taoche.com/pinggu/pricesearch.aspx?t=7&b=%s&s=%s&c=%s&y=%s&m=0.1" % (brand_ex_id, car.serial.ex_id,
                                                                                               car.ex_id, "%s-04" % year)
        for j in range(3):
            try:
                text = requests.get(url, timeout=10, headers=headers).text
            except:
                pass
            break
        text = pq(text)
        words = text(".pgcxtit p").html().strip()
        print car.id, words.encode("utf8")
        words = words.split(u"指导价")[1]

        if u"万" in words:
            original_price = float(words.replace(u"万", ""))
        car.original_price = original_price
        car.img = text(".pgyh_pic img").attr("src")
        car.save()

        if i % 100 == 0:
            print i, datetime.datetime.now()


if __name__ == '__main__':
    # get_brand()
    # get_serial()
    # get_car_basic_info()
    get_car_original_price()
