# -*- coding: utf-8 -*-

import datetime
import logging
import time
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache, raw_sql
from www.misc.decorators import cache_required
from www.misc import consts

from models import Item, Company, Meal, MealItem

DEFAULT_DB = 'default'

dict_err = {
    20101: u'茶点产品名重复',
    20102: u'没有找到对应的茶点产品',
    20201: u'公司名称重复',
    20202: u'没有找到对应的公司',
    20301: u'套餐名称重复',
    20302: u'没有找到对应的套餐',
}
dict_err.update(consts.G_DICT_ERROR)

class ItemBase(object):

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
                sort = sort
            )

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, item

    def search_items_for_admin(self, name):
        objs = self.get_all_item()
        
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

    def add_company(self, name, staff_name, mobile, tel, addr, city_id, sort, des):

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
                des = des
            )
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

    def modify_company(self, company_id, name, staff_name, mobile, tel, addr, city_id, sort, des, state):
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
            print meal_items
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














