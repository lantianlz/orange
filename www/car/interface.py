# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
import requests, re, random

from django.db.models import Count

from common import debug
from www.misc import consts
from www.car.models import Brand, CarBasicInfo, Serial, UserUsedCar

dict_err = {
    20100: u'',
}
dict_err.update(consts.G_DICT_ERROR)


class BrandBase(object):

    def __init__(self):
        pass

    def get_city_by_id(self, city_id):
        if city_id:
            citys = self.get_all_citys().filter(id=city_id)
            if citys:
                return citys[0]

    def get_city_by_name(self, city_name):
        objs = self.get_all_citys().filter(city=city_name)
        if objs:
            return objs[0]
        return None

    def get_all_brand(self, state=None):
        objs = Brand.objects.all()

        if state:
            objs = objs.filter(state=state)

        return objs

    def get_all_parent_brand(self, state=None):
        objs = self.get_all_brand(state)

        return objs.filter(parent_brand__isnull=True)

    def get_children_brand(self, parent_id, state=None):
        objs = self.get_all_brand(state)

        return objs.filter(parent_brand__id=parent_id)


class SerialBase(object):

    def __init__(self):
        pass

    def get_all_serial(self, state=None):
        objs = Serial.objects.all()

        if state:
            objs = objs.filter(state=state)

        return objs

    def get_serial_by_brand(self, brand_id, state=None):
        '''
        获取品牌下的车系
        '''
        objs = self.get_all_serial()
        brand_ids = []
        # 获取品牌列表
        brands = BrandBase().get_children_brand(brand_id, True)

        if brands:
            brand_ids = [x.id for x in brands]
        else:
            brand_ids = [brand_id]

        return objs.filter(brand__in=brand_ids)

    def get_serial_by_id(self, id, state=None):
        return self.get_all_serial(state).filter(id=id)


class CarBasicInfoBase(object):

    def __init__(self):
        pass

    def get_all_car_basic_info(self, state=None):
        objs = CarBasicInfo.objects.all()

        if state:
            objs = objs.filter(state=state)

        return objs

    def get_car_basic_info_by_serial(self, serial_id, state=None):
        objs = self.get_all_car_basic_info(state)

        return objs.filter(serial__id=serial_id)

    def get_car_basic_info_by_id(self, id, state=None):
        return self.get_all_car_basic_info(state).filter(id=id)


class UserUsedCarBase(object):

    def __init__(self):
        pass

    def get_all_user_used_car(self):
        return UserUsedCar.objects.all()

    def get_top_20_history(self):
        objs = self.get_all_user_used_car().filter(price__gt=0).order_by('-create_time')
        return objs[:20]

    def evaluate_price(self, car_basic_info_id, get_license_time, trip_distance, ip):
        price = self.get_yiche_price(car_basic_info_id, get_license_time, trip_distance)
        obj = None
        try:
            obj = UserUsedCar.objects.create(
                car_id = car_basic_info_id,
                get_license_time = get_license_time,
                trip_distance = trip_distance,
                ip = ip,
                price = price
            )

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900), price

        return 0, obj, price

    def get_yiche_price(self, car_basic_info_id, get_license_time, trip_distance):
        '''
        获取易车网价格
        '''
        price = 0.0
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0"}
        try:
            car = CarBasicInfoBase().get_car_basic_info_by_id(car_basic_info_id)
            if not car:
                return price
            car = car[0]
            brand = car.serial.brand
            brand_ex_id = brand.ex_id or brand.parent_brand.ex_id
            year = get_license_time.strftime('%Y-%m-%d')

            url = "http://www.taoche.com/pinggu/pricesearch.aspx?t=7&b=%s&s=%s&c=%s&y=%s&m=%s" % (brand_ex_id, car.serial.ex_id,
                                                                                               car.ex_id, year, trip_distance)
            
            for i in range(3):
                try:
                    rep = requests.get(url, timeout=7, headers=headers)
                    break
                except Exception, e:
                    pass

            text = pq(rep.text)
            
            price = re.search('\d+.?\d+', text('.cegnjj').find('strong').text()).group()
            
            # 价格浮动
            price = float(price) + round(random.uniform(-0.2, 0.2), 2)
        except Exception, e:
            debug.get_debug_detail(e)

        return float(price)

    def sell_car(self, user_used_car_id, mobile):
        obj = UserUsedCar.objects.filter(id=user_used_car_id)
        if obj:
            obj = obj[0]

        try:
            obj.mobile = mobile
            obj.save()

            from www.tasks import async_send_email
            title = u"生意来了，有人要卖车"
            content = u"手机用户 [ %s ] 要卖 [ %s - %s ], 新车价[ %s 万], 估价[ %s 万] " % (mobile, obj.car.serial.name, obj.car.name, obj.car.original_price, obj.price)
            async_send_email(["web@aoaoxc.com", "200581107@qq.com"], title, content)
            
        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_top_5_evaluate_car(self):
        return UserUsedCar.objects.all().values('car__serial__name').annotate(total=Count('car__serial__name')).order_by('-total')[:5]