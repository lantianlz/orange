# -*- coding: utf-8 -*-

import datetime
import logging
import time
import random
import decimal
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache, raw_sql
from www.misc.decorators import cache_required
from www.misc import consts

from models import Item, Company, Meal, MealItem, Order, OrderItem, Booking

DEFAULT_DB = 'default'

dict_err = {
    20101: u'茶点产品名重复',
    20102: u'没有找到对应的茶点产品',

    20201: u'公司名称重复',
    20202: u'没有找到对应的公司',

    20301: u'套餐名称重复',
    20302: u'没有找到对应的套餐',

    20401: u'没有找到对应的订单',

    20501: u'该手机号已经预约',
    20502: u'没有找到对应的预约信息',
}
dict_err.update(consts.G_DICT_ERROR)

class ItemBase(object):

    def generate_item_code(self, item_type):
        '''
        自动生成货号
        '''
        word = Item.code_dict[int(item_type)]
        count = Item.objects.filter(item_type=item_type).count() + 1
        count = '%03d' % count

        return word + count

    def get_all_item(self, state=None):
        objs = Item.objects.all()

        if state != None:
            objs = objs.filter(state=state)

        return objs

    def add_item(self, name, item_type, spec, price, sort):

        if not (name and item_type and price):
            return 99800, dict_err.get(99800)

        if Item.objects.filter(name=name):
            return 20101, dict_err.get(20101)
        
        try:
            item = Item.objects.create(
                name = name,
                item_type = item_type,
                spec = spec,
                price = price,
                sort = sort,
                code = self.generate_item_code(item_type)
            )

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, item

    def search_items_for_admin(self, item_type, name):
        objs = self.get_all_item()
        
        if item_type != -1:
            objs = objs.filter(item_type=item_type)

        if name:
            objs = objs.filter(name__contains=name)
        
        return objs

    def get_item_by_id(self, item_id):
        obj = self.get_all_item().filter(id=item_id)

        if obj:
            obj = obj[0]

        return obj

    def modify_item(self, item_id, name, item_type, spec, price, sort, state):
        
        if not (name and item_type and price):
            return 99800, dict_err.get(99800)

        obj = Item.objects.filter(id=item_id)
        if not obj:
            return 20102, dict_err.get(20102)
        obj = obj[0]

        temp = Item.objects.filter(name=name)
        if temp and temp[0].id != obj.id:
            return 20103, dict_err.get(20103)

        try:
            obj.name = name
            obj.item_type = item_type
            obj.spec = spec
            obj.price = price
            obj.sort = sort
            obj.state = state
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_items_by_name(self, name):
        objs = self.get_all_item(1)
        
        if name:
            objs = objs.filter(name__contains=name)
        
        return objs

class CompanyBase(object):

    def get_all_company(self, state=None):
        objs = Company.objects.all()

        if state != None:
            objs = objs.filter(state=state)

        return objs

    def search_companys_for_admin(self, name):
        objs = self.get_all_company()

        if name:
            objs = objs.filter(name__contains=name)

        return objs

    def get_company_by_id(self, id):
        try:
            ps = dict(id=id)

            return Company.objects.get(**ps)
        except Company.DoesNotExist:
            return ""

    def add_company(self, name, staff_name, mobile, tel, addr, city_id, sort, des, person_count):

        if not (name and staff_name and mobile and addr and city_id):
            return 99800, dict_err.get(99800)

        if Company.objects.filter(name=name):
            return 20201, dict_err.get(20201)

        try:
            obj = Company.objects.create(
                name = name,
                staff_name = staff_name,
                mobile = mobile,
                tel = tel,
                addr = addr,
                city_id = city_id,
                sort = sort,
                des = des,
                person_count = person_count
            )
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

    def modify_company(self, company_id, name, staff_name, mobile, tel, addr, city_id, sort, des, state, person_count):
        if not (name and staff_name and mobile and addr and city_id):
            return 99800, dict_err.get(99800)

        obj = self.get_company_by_id(company_id)
        if not obj:
            return 20202, dict_err.get(20202)

        if obj.name != name and Company.objects.filter(name=name):
            return 20201, dict_err.get(20201)

        try:
            obj.name = name
            obj.staff_name = staff_name
            obj.mobile = mobile
            obj.tel = tel
            obj.addr = addr
            obj.city_id = city_id
            obj.sort = sort
            obj.des = des
            obj.state = state
            obj.person_count = person_count
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)
        
        return 0, dict_err.get(0)

    def get_companys_by_name(self, name=""):
        objs = self.get_all_company()

        if name:
            objs = objs.filter(name__contains=name)

        return objs[:10]

class MealBase(object):

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_meal(self, company_id, name, price, start_date, end_date, des='', meal_items=[]):
        if not (company_id and name and price and start_date and end_date):
            return 99800, dict_err.get(99800)

        if not CompanyBase().get_company_by_id(company_id):
            return 20202, dict_err.get(20202)

        try:
            # 套餐
            meal = Meal.objects.create(
                company_id = company_id,
                name = name,
                price = price,
                start_date = start_date,
                end_date = end_date,
                des = des
            )

            # 套餐下的项目
            for x in meal_items:
                MealItem.objects.create(
                    meal = meal,
                    item_id = x['item_id'],
                    amount = x['amount']
                )
            
            transaction.commit(using=DEFAULT_DB)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

        return 0, meal

    @transaction.commit_manually(using=DEFAULT_DB)
    def modify_meal(self, meal_id, company_id, name, price, start_date, end_date, des='', meal_items=[]):
        if not (company_id and name and price and start_date and end_date):
            return 99800, dict_err.get(99800)

        obj = self.get_meal_by_id(meal_id)
        if not obj:
            return 20302, dict_err.get(20302)

        if not CompanyBase().get_company_by_id(company_id):
            return 20202, dict_err.get(20202)

        if obj.name != name and Meal.objects.filter(name=name):
            return 20301, dict_err.get(20301)

        try:
            # 套餐
            obj.company_id = company_id
            obj.name = name
            obj.price = price
            obj.start_date = start_date
            obj.end_date = end_date
            obj.des = des
            obj.save()

            # 套餐下的项目
            MealItem.objects.filter(meal=obj).delete()

            for x in meal_items:
                MealItem.objects.create(
                    meal = obj,
                    item_id = x['item_id'],
                    amount = x['amount']
                )
            
            transaction.commit(using=DEFAULT_DB)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_all_meal(self, state=None):
        objs = Meal.objects.all()

        if state != None:
            objs = objs.filter(state=state)

        return objs

    def search_meals_for_admin(self, name):
        objs = self.get_all_meal()

        if name:
            objs = objs.filter(name__contains=name)

        return objs

    def get_meal_by_id(self, meal_id):
        try:
            ps = dict(id=meal_id)

            return Meal.objects.get(**ps)
        except Meal.DoesNotExist:
            return ""

    def get_items_of_meal(self, meal_id):
        return MealItem.objects.filter(meal_id=meal_id)

    def get_meals_by_name(self, name=""):
        objs = self.get_all_meal()

        if name:
            objs = objs.filter(name__contains=name)

        return objs[:10]

class OrderBase(object):

    def generate_order_no(self, pr):
        """
        @note: 生成订单的id，传入不同前缀来区分订单类型
        """
        postfix = '%s' % datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]  # 纯数字
        if pr:
            postfix = '%s%s%02d' % (pr, postfix, random.randint(0, 99))
        return postfix

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_order(self, meal_id, create_operator, total_price, order_items, is_test=False, note=''):
        
        if not (meal_id and create_operator and total_price and order_items):
            return 99800, dict_err.get(99800)

        meal = MealBase().get_meal_by_id(meal_id)            
        if not meal:
            return 20302, dict_err.get(20302)

        if not CompanyBase().get_company_by_id(meal.company_id):
            return 20202, dict_err.get(20202)

        try:
            # 订单
            obj = Order.objects.create(
                meal_id = meal.id,
                company_id = meal.company_id,
                order_no = self.generate_order_no("T"),
                create_operator = create_operator,
                total_price = total_price,
                is_test = is_test,
                note = note
            )

            # 订单下的项目
            for x in order_items:

                item = ItemBase().get_item_by_id(x['item_id'])

                OrderItem.objects.create(
                    order = obj,
                    item_id = x['item_id'],
                    amount = x['amount'],
                    price = item.price,
                    total_price = item.price * decimal.Decimal(x['amount'])
                )
            
            transaction.commit(using=DEFAULT_DB)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

        return 0, obj

    def get_all_order(self, state=None):
        objs = Order.objects.all()

        if state != None:
            objs = objs.filter(state=state)

        return objs

    def search_orders_for_admin(self, start_date, end_date, state, order_no):

        if order_no:
            objs = self.get_all_order().filter(order_no=order_no)
        else:
            objs = self.get_all_order(state).filter(
                create_time__range = (start_date, end_date)
            )

        return objs

    def search_uncreate_orders_for_admin(self, start_date, end_date):
        # 查询出日期需要配送的套餐
        objs = MealBase().get_all_meal(state=1).filter(
            end_date__gt = end_date
        )
        meal_ids = [x.id for x in objs]

        # 查询日期已经配送的订单
        orders = Order.objects.filter(
            create_time__range = (start_date, end_date),
            meal_id__in = meal_ids
        ).exclude(state=0)
        except_meal_ids = [x.meal_id for x in orders]

        # 排除掉已经送出的订单
        objs = objs.exclude(id__in = except_meal_ids)

        return objs

    def get_order_by_id(self, order_id):
        try:
            ps = dict(id=order_id)

            return Order.objects.get(**ps)
        except Meal.DoesNotExist:
            return ""

    def distribute_order(self, order_id, distribute_operator):

        obj = self.get_order_by_id(order_id)
        if not obj:
            return 20401, dict_err.get(20401)

        try:
            obj.state = 2
            obj.distribute_operator = distribute_operator
            obj.distribute_time = datetime.datetime.now()
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def confirm_order(self, order_id, confirm_operator):

        obj = self.get_order_by_id(order_id)
        if not obj:
            return 20401, dict_err.get(20401)

        try:
            obj.state = 3
            obj.confirm_operator = confirm_operator
            obj.confirm_time = datetime.datetime.now()
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def drop_order(self, order_id):

        obj = self.get_order_by_id(order_id)
        if not obj:
            return 20401, dict_err.get(20401)

        try:
            obj.state = 0
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_items_of_order(self, order_id):
        return OrderItem.objects.filter(order_id=order_id)


class BookingBase(object):

    def get_booking_by_id(self, booking_id):
        try:
            ps = dict(id=booking_id)

            return Booking.objects.get(**ps)
        except Booking.DoesNotExist:
            return ""

    def add_booking(self, company_name, staff_name, mobile, source=1):

        if not (company_name and staff_name and mobile):
            return 99800, dict_err.get(99800)

        if Booking.objects.filter(mobile=mobile):
            return 20501, dict_err.get(20501)

        try:
            obj = Booking.objects.create(
                company_name = company_name,
                staff_name = staff_name,
                mobile = mobile,
                source = source
            )
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

    def modify_booking(self, booking_id, operator_id, state, note=''):

        if not (booking_id and operator_id and state):
            return 99800, dict_err.get(99800)

        obj = self.get_booking_by_id(booking_id)
        if not obj:
            return 20502, dict_err.get(20502)

        try:

            obj.note = note
            obj.state = state
            obj.operator_id = operator_id
            obj.operation_time = datetime.datetime.now()
            obj.save()

        except Exception, e:
            import traceback
            traceback.print_exc()
            # debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def search_bookings_for_admin(self, state):
        return Booking.objects.filter(state=state)












