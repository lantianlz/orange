# -*- coding: utf-8 -*-

import datetime
import logging
import time
import random
import decimal
from django.db import transaction
from django.db.models import Sum
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache, raw_sql
from www.misc.decorators import cache_required
from www.misc import consts

from www.account.interface import UserBase, ExternalTokenBase
from models import Item, Company, Meal, MealItem, Order, OrderItem, \
    Booking, CompanyManager, CashAccount, CashRecord, Supplier, \
    SupplierCashAccount, SupplierCashRecord, PurchaseRecord, SaleMan

DEFAULT_DB = 'default'

dict_err = {
    20101: u'茶点产品名重复',
    20102: u'没有找到对应的茶点产品',

    20201: u'公司名称重复',
    20202: u'没有找到对应的公司',
    20203: u'销售日期不能小于创建日期',

    20301: u'套餐名称重复',
    20302: u'没有找到对应的套餐',

    20401: u'没有找到对应的订单',

    20501: u'已预约，请勿重复提交',
    20502: u'没有找到对应的预约信息',

    20601: u'该管理员已存在，请勿重复添加',

    20701: u'没有找到对应的账户信息',
    20702: u'账户余额不足',

    20801: u'供货商名称重复',
    20801: u'没有找到对应的供货商',

    20901: u'没有找到对应的采购流水',

    21001: u'没有找到对应的销售人员',
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

    def add_item(self, name, item_type, spec, price, sort, integer, sale_price, init_add, supplier_id, des):

        if not (name and item_type and price and supplier_id):
            return 99800, dict_err.get(99800)

        if not SupplierBase().get_supplier_by_id(supplier_id):
            return 20802, dict_err.get(20802)

        if Item.objects.filter(name=name):
            return 20101, dict_err.get(20101)

        try:
            item = Item.objects.create(
                name=name,
                item_type=item_type,
                spec=spec,
                price=price,
                sort=sort,
                integer=integer,
                sale_price=sale_price,
                init_add=init_add,
                supplier_id=supplier_id,
                des=des,
                code=self.generate_item_code(item_type)
            )

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, item

    def search_items_for_admin(self, item_type, supplier, name):
        objs = self.get_all_item()

        if item_type != -1:
            objs = objs.filter(item_type=item_type)

        if supplier:
            objs = objs.select_related('supplier').filter(supplier__name__contains=supplier)

        if name:
            objs = objs.filter(name__contains=name)

        return objs

    def get_item_by_id(self, item_id):
        obj = self.get_all_item().filter(id=item_id)

        if obj:
            obj = obj[0]

        return obj

    def modify_item(self, item_id, name, item_type, spec, price, sort, state, integer, sale_price, init_add, supplier_id, des):

        if not (name and item_type and price and supplier_id):
            return 99800, dict_err.get(99800)

        if not SupplierBase().get_supplier_by_id(supplier_id):
            return 20802, dict_err.get(20802)

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
            obj.integer = integer
            obj.init_add = init_add
            obj.sale_price = sale_price
            obj.supplier_id = supplier_id
            obj.des = des
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_items_by_name(self, name):
        objs = self.get_all_item(True)

        if name:
            objs = objs.filter(name__contains=name)

        return objs

    def get_init_add_items(self):
        return self.get_all_item(True).filter(init_add=1)


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

    def add_company(self, name, staff_name, mobile, tel, addr, city_id, \
        sort, des, person_count, invite_by, is_show, logo, short_name, sale_date, sale_by):

        if not (name and staff_name and mobile and addr and city_id):
            return 99800, dict_err.get(99800)

        if Company.objects.filter(name=name):
            return 20201, dict_err.get(20201)

        invite = None
        if invite_by:
            invite = UserBase().get_user_by_id(invite_by)

        if sale_date:
            sale_date = datetime.datetime.strptime(sale_date, '%Y-%m-%d')
            if sale_date < datetime.datetime.now():
                return 20203, dict_err.get(20203)

        try:
            obj = Company.objects.create(
                name=name,
                staff_name=staff_name,
                mobile=mobile,
                tel=tel,
                addr=addr,
                city_id=city_id,
                sort=sort,
                des=des,
                person_count=person_count,
                invite_by=invite.id if invite else None,
                is_show=is_show,
                logo=logo,
                short_name=short_name,
                sale_date = sale_date,
                sale_by = sale_by
            )

            # 创建公司对应的账户
            CashAccount.objects.create(company=obj)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

    def modify_company(self, company_id, name, staff_name, mobile, tel, \
        addr, city_id, sort, des, state, person_count, invite_by, \
        is_show, logo, short_name, sale_date, sale_by):
        if not (name and staff_name and mobile and addr and city_id):
            return 99800, dict_err.get(99800)

        obj = self.get_company_by_id(company_id)
        if not obj:
            return 20202, dict_err.get(20202)

        if obj.name != name and Company.objects.filter(name=name):
            return 20201, dict_err.get(20201)

        invite = None
        if invite_by:
            invite = UserBase().get_user_by_id(invite_by)

        if sale_date:
            sale_date = datetime.datetime.strptime(sale_date, '%Y-%m-%d')
            if sale_date < obj.create_time:
                return 20203, dict_err.get(20203)

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
            obj.invite_by = invite.id if invite else None
            obj.is_show = is_show 
            obj.logo = logo 
            obj.short_name = short_name
            obj.sale_date = sale_date
            obj.sale_by = sale_by
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

    def get_companys_by_show(self):
        return self.get_all_company(state=True).filter(is_show=1).order_by('-sort', 'id')


class MealBase(object):

    def _get_cycle_str(self, cycle):
        temp = []
        for x in range(1, 8):
            temp.append(str(x)) if str(x) in cycle else temp.append('0')
        
        return "-".join(temp)

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_meal(self, company_id, name, price, start_date, end_date, cycle, des='', meal_items=[]):
        if not (company_id and name and price and start_date and end_date and cycle):
            return 99800, dict_err.get(99800)

        if not CompanyBase().get_company_by_id(company_id):
            return 20202, dict_err.get(20202)

        try:
            # 套餐
            meal = Meal.objects.create(
                company_id=company_id,
                name=name,
                price=price,
                start_date=start_date,
                end_date=end_date,
                cycle=self._get_cycle_str(cycle),
                des=des
            )

            # 套餐下的项目
            for x in meal_items:
                MealItem.objects.create(
                    meal=meal,
                    item_id=x['item_id'],
                    amount=x['amount']
                )

            transaction.commit(using=DEFAULT_DB)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

        return 0, meal

    @transaction.commit_manually(using=DEFAULT_DB)
    def modify_meal(self, meal_id, company_id, name, price, start_date, end_date, state, cycle, des='', meal_items=[]):
        if not (company_id and name and price and start_date and end_date and cycle):
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
            obj.state = state
            obj.cycle = self._get_cycle_str(cycle)
            obj.save()

            # 套餐下的项目
            MealItem.objects.filter(meal=obj).delete()

            for x in meal_items:
                MealItem.objects.create(
                    meal=obj,
                    item_id=x['item_id'],
                    amount=x['amount']
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

    def search_meals_for_admin(self, state, name):
        objs = self.get_all_meal(state)

        if name:
            objs = objs.filter(name__contains=name)

        return objs

    def get_meal_by_id(self, meal_id):
        try:
            ps = dict(id=meal_id)

            return Meal.objects.get(**ps)
        except Meal.DoesNotExist:
            return ""

    def get_meals_by_name(self, name=""):
        objs = self.get_all_meal()

        if name:
            objs = objs.filter(name__contains=name)

        return objs[:10]

    def get_meal_by_company(self, company_id):
        objs = self.get_all_meal(True).filter(company_id=company_id)
        if objs:
            return objs[0]

    def get_items_of_meal(self, meal_id):
        '''
        获取订单下的项目
        '''
        if meal_id:
            return MealItem.objects.select_related('item').filter(meal_id=meal_id)
        else:
            return []


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
                meal_id=meal.id,
                company_id=meal.company_id,
                order_no=self.generate_order_no("T"),
                create_operator=create_operator,
                total_price=total_price,
                is_test=is_test,
                note=note
            )

            temp = decimal.Decimal(0)

            # 订单下的项目
            for x in order_items:

                item = ItemBase().get_item_by_id(x['item_id'])

                # 计算成本价
                temp += item.price * decimal.Decimal(x['amount'])

                OrderItem.objects.create(
                    order=obj,
                    item_id=x['item_id'],
                    amount=x['amount'],
                    price=item.price,
                    sale_price=item.sale_price,
                    total_price=item.price * decimal.Decimal(x['amount']),
                    total_sale_price=item.sale_price * decimal.Decimal(x['amount'])
                )

            # 计算成本价
            obj.cost_price = temp
            obj.save()

            transaction.commit(using=DEFAULT_DB)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

        return 0, obj

    @transaction.commit_manually(using=DEFAULT_DB)
    def modify_order(self, order_id, order_items, total_price, note, is_test):

        obj = self.get_order_by_id(order_id)
        if not obj:
            return 20401, dict_err.get(20401)

        try:
            obj.total_price = total_price
            obj.note = note
            obj.is_test = is_test

            temp = decimal.Decimal(0)

            # 订单下的项目
            OrderItem.objects.filter(order=obj).delete()
            for x in order_items:

                item = ItemBase().get_item_by_id(x['item_id'])

                # 计算成本价
                temp += item.price * decimal.Decimal(x['amount'])

                OrderItem.objects.create(
                    order=obj,
                    item_id=x['item_id'],
                    amount=x['amount'],
                    price=item.price,
                    sale_price=item.sale_price,
                    total_price=item.price * decimal.Decimal(x['amount']),
                    total_sale_price=item.sale_price * decimal.Decimal(x['amount'])
                )

            # 计算成本价
            obj.cost_price = temp
            obj.save()

            transaction.commit(using=DEFAULT_DB)
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_all_order(self, state=None):
        objs = Order.objects.all()

        if state != None:
            objs = objs.filter(state=state)

        return objs

    def search_orders_for_admin(self, start_date, end_date, state, company):
        
        # 是否查询所有有效订单
        if state == -2:
            objs = Order.objects.filter(
                state__in=(1, 2, 3)
            )
        else:
            objs = self.get_all_order(state)

        objs = objs.select_related('company').filter(
            create_time__range=(start_date, end_date),
            company__name__contains=company
        )

        return objs

    def search_uncreate_orders_for_admin(self, start_date, end_date):
        # 查询出日期需要配送的套餐
        objs = MealBase().get_all_meal(state=1).filter(
            end_date__gt=end_date
        )
        meal_ids = [x.id for x in objs]

        # 查询日期已经配送的订单
        orders = Order.objects.filter(
            create_time__range=(start_date, end_date),
            meal_id__in = meal_ids
        ).exclude(state=0)
        except_meal_ids = [x.meal_id for x in orders]

        # 排除掉已经送出的订单
        objs = objs.exclude(id__in=except_meal_ids)

        return objs

    def get_order_by_id(self, order_id):
        try:
            ps = dict(id=order_id)

            return Order.objects.get(**ps)
        except Meal.DoesNotExist:
            return ""

    def distribute_order(self, order_id, distribute_operator):
        '''
        配送订单
        '''
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

    @transaction.commit_manually(using=DEFAULT_DB)
    def confirm_order(self, order_id, confirm_operator, ip=None):
        '''
        确认订单
        '''
        obj = self.get_order_by_id(order_id)
        if not obj:
            return 20401, dict_err.get(20401)

        try:
            obj.state = 3
            obj.confirm_operator = confirm_operator
            obj.confirm_time = datetime.datetime.now()
            obj.save()

            # 试吃订单不操作账户
            if obj.is_test:
                transaction.commit(using=DEFAULT_DB)
            else:
                code, msg = CashRecordBase().add_cash_record(
                    obj.company_id,
                    obj.total_price,
                    1,
                    u"订单「%s」确认" % obj.order_no,
                    ip
                )

                if code == 0:
                    transaction.commit(using=DEFAULT_DB)
                else:
                    transaction.rollback(using=DEFAULT_DB)
                    return code, dict_err.get(code)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def drop_order(self, order_id):
        '''
        作废订单
        '''
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
        '''
        获取订单下的项目
        '''
        return OrderItem.objects.select_related('item').filter(order_id=order_id)

    def get_purchase(self, start_date, end_date, state):
        objs = []

        states = []
        # 是否查询所有有效订单
        if state == -2:
            states = [1, 2, 3]
        else:
            states = [state]

        objs = OrderItem.objects.select_related('order', 'item', 'order__company', 'item__supplier').filter(
            order__state__in=states,
            order__create_time__range=(start_date, end_date)
        ).values(
            'order__order_no', 'order__create_time',
            'order__company__name', 'item__code',
            'item__name', 'amount', 'item__des',
            'item__spec', 'item__item_type',
            'item__supplier__id', 'item__supplier__name'
        )

        return objs


    def search_orders_by_company(self, company_id, start_date, end_date, order_no):
        '''
        公司平台查询订单
        '''
        objs = Order.objects.filter(
            company_id = company_id,
            state__in=(1, 2, 3)
        )

        if order_no:
            objs = objs.filter(order_no=order_no)
        else:
            objs = objs.filter(create_time__range=(start_date, end_date))

        return objs

    @cache_required(cache_key='active_order_count', expire=43200, cache_config=cache.CACHE_TMP)
    def get_active_order_count(self):
        '''
        获取有效订单数量
        '''
        return Order.objects.filter(state=3).count()

    @cache_required(cache_key='active_person_time_count', expire=43200, cache_config=cache.CACHE_TMP)
    def get_active_person_time_count(self):
        '''
        获取有效人次
        '''
        objs = Order.objects.select_related('company').filter(state=3)
        return objs.aggregate(Sum('company__person_count'))['company__person_count__sum']

    def get_purchase_statement(self, name, start_date, end_date):
        '''
        根据订单按供货商查询汇总信息
        '''
        sql = """
            SELECT c.supplier_id, d.name, sum(b.total_price), a.order_no, a.confirm_time, e.name, a.id
            FROM company_order AS a, company_orderitem AS b, company_item AS c, company_supplier AS d, company_company AS e
            WHERE a.id = b.order_id 
            AND d.id = c.supplier_id 
            AND b.item_id = c.id 
            AND a.state = 3 
            AND a.company_id = e.id
            AND d.name like %s 
            AND a.confirm_time > %s 
            AND a.confirm_time < %s 
            GROUP BY c.supplier_id, a.order_no
        """
        
        return raw_sql.exec_sql(sql, ['%%%s%%' % name, str(start_date), str(end_date)])


class BookingBase(object):

    def get_booking_by_id(self, booking_id):
        try:
            ps = dict(id=booking_id)

            return Booking.objects.get(**ps)
        except Booking.DoesNotExist:
            return ""

    def add_booking(self, company_name, staff_name, mobile, source=0, invite_by=None):

        if not (company_name and staff_name and mobile):
            return 99800, dict_err.get(99800)

        if Booking.objects.filter(mobile=mobile) or Booking.objects.filter(company_name=company_name):
            return 20501, dict_err.get(20501)

        # 邀请人
        invite = None
        if invite_by:
            invite = UserBase().get_user_by_id(invite_by)

        try:
            obj = Booking.objects.create(
                company_name=company_name,
                staff_name=staff_name,
                mobile=mobile,
                source=source,
                invite_by=invite.id if invite else None
            )

            # 发送邮件提醒
            from www.tasks import async_send_email

            sources = dict(Booking.source_choices)
            title = u'诸位，订单来了'
            content = u'「%s」的「%s」通过「%s」申请预订，联系电话「%s」' % (company_name, staff_name, sources.get(int(source), u'未知'), mobile)
            async_send_email("vip@3-10.cc", title, content)

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
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def search_bookings_for_admin(self, state):
        return Booking.objects.filter(state=state)


class CompanyManagerBase(object):

    def get_cm_by_user_id(self, user_id):
        """
        @note: 获取用户管理的第一个公司，用于自动跳转到管理的公司
        """
        cms = list(CompanyManager.objects.select_related("company").filter(user_id=user_id))
        if cms:
            return cms[0]

    def check_user_is_cm(self, company_id, user):
        """
        @note: 判断用户是否是某个公司管理员
        """
        if isinstance(user, (str, unicode)):
            user = UserBase().get_user_by_id(user)

        cm = CompanyManager.objects.filter(company__id=company_id, user_id=user.id)

        return True if (cm or user.is_staff()) else False

    def add_company_manager(self, company_id, user_id):
        if not (company_id and user_id):
            return 99800, dict_err.get(99800)

        if user_id and not UserBase().get_user_login_by_id(user_id):
            return 99600, dict_err.get(99600)

        if CompanyManager.objects.filter(user_id=user_id, company__id=company_id):
            return 20601, dict_err.get(20601)

        try:
            cm = CompanyManager.objects.create(user_id=user_id, company_id=company_id)
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, cm

    def search_managers_for_admin(self, company_name):
        objs = CompanyManager.objects.select_related("company").all()

        if company_name:
            objs = objs.filter(company__name__contains=company_name)

        return objs

    def get_manager_by_id(self, manager_id):
        try:
            return CompanyManager.objects.select_related("company").get(id=manager_id)
        except CompanyManager.DoesNotExist:
            return ''

    def delete_company_manager(self, manager_id):
        if not manager_id:
            return 99800, dict_err.get(99800)

        try:
            CompanyManager.objects.get(id=manager_id).delete()
        except Exception:
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_managers_by_company(self, company_id):
        return CompanyManager.objects.filter(company_id = company_id)


class CashAccountBase(object):

    '''
    '''

    def get_all_accounts(self):
        return CashAccount.objects.all()

    def get_accounts_for_admin(self, name):
        objs = self.get_all_accounts()

        if name:
            objs = objs.select_related('company').filter(company__name__contains=name)

        return objs

    def get_cash_account_by_id(self, account_id):
        try:
            return CashAccount.objects.select_related("company").get(id=account_id)
        except CashAccount.DoesNotExist:
            return ''

    def modify_cash_account(self, account_id, max_overdraft):

        obj = self.get_cash_account_by_id(account_id)
        if not obj:
            return 20701, dict_err.get(20701)

        try:
            obj.max_overdraft = max_overdraft
            obj.save()
        except Exception:
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_account_by_company(self, company_id):
        try:
            return CashAccount.objects.get(company_id=company_id)
        except CashAccount.DoesNotExist:
            return ''

class CashRecordBase(object):

    def send_balance_insufficient_notice(self, company, balance, max_overdraft):
        # 发送邮件提醒
        from www.tasks import async_send_email
        title = u'账户已达最高透支额'
        content = u'账户「%s」当前余额「%.2f」元，已达「%.2f」元最高透支额，请联系充值' % (company.name, balance, max_overdraft)
        async_send_email("vip@3-10.cc", title, content)

        # 发送微信提醒
        from weixin.interface import WeixinBase
        for manager in CompanyManagerBase().get_managers_by_company(company.id):
            
            to_user_openid = ExternalTokenBase().get_weixin_openid_by_user_id(manager.user_id)

            if to_user_openid:
                WeixinBase().send_balance_insufficient_template_msg(
                    to_user_openid, u"账户已达「%.2f」元最高透支额，请联系充值" % max_overdraft, 
                    company.name, u"%.2f 元" % balance, 
                    u"感谢您的支持，祝工作愉快"
                )

    def send_recharge_success_notice(self, company, amount, balance):
        # 发送邮件提醒
        from www.tasks import async_send_email
        title = u'账户充值成功'
        content = u'账户「%s」成功充值「%.2f」元，当前余额「%.2f」元。' % (company.name, amount, balance)
        async_send_email("vip@3-10.cc", title, content)

        # 发送微信提醒
        from weixin.interface import WeixinBase
        for manager in CompanyManagerBase().get_managers_by_company(company.id):
            
            to_user_openid = ExternalTokenBase().get_weixin_openid_by_user_id(manager.user_id)

            if to_user_openid:
                WeixinBase().send_recharge_success_template_msg(
                    to_user_openid, 
                    u"%s，您已成功充值" % company.name,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 
                    u"%.2f 元" % amount, 
                    u"账户余额：%.2f 元" % balance
                )

    def get_all_records(self, operation=None):
        objs = CashRecord.objects.all()
        if operation:
            objs = objs.filter(operation=operation)

        return objs

    def get_records_for_admin(self, start_date, end_date, name, operation=None):
        objs = self.get_all_records(operation).filter(create_time__range=(start_date, end_date))

        if name:
            objs = objs.filter(cash_account__company__name__contains=name)

        return objs, objs.aggregate(Sum('value'))['value__sum']

    def validate_record_info(self, company_id, value, operation, notes):
        value = float(value)
        operation = int(operation)
        company = CompanyBase().get_company_by_id(company_id)
        assert operation in (0, 1)
        assert value > 0 and notes and company

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_cash_record_with_transaction(self, company_id, value, operation, notes, ip=None):
        try:
            errcode, errmsg = self.add_cash_record(company_id, value, operation, notes, ip)
            if errcode == 0:
                transaction.commit(using=DEFAULT_DB)
            else:
                transaction.rollback(using=DEFAULT_DB)
            return errcode, errmsg
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    def add_cash_record(self, company_id, value, operation, notes, ip=None):
        try:
            try:
                value = decimal.Decimal(value)
                operation = int(operation)
                self.validate_record_info(company_id, value, operation, notes)
            except Exception, e:
                return 99801, dict_err.get(99801)

            account, created = CashAccount.objects.get_or_create(company_id=company_id)

            if operation == 0:
                account.balance += value
            elif operation == 1:
                account.balance -= value
            account.save()

            CashRecord.objects.create(
                cash_account=account,
                value=value,
                current_balance=account.balance,
                operation=operation,
                notes=notes,
                ip=ip
            )

            # 转出时判断是否超过透支额  发送提醒
            if operation == 1 and account.balance < 0 and abs(account.balance) >= account.max_overdraft:
                self.send_balance_insufficient_notice(
                    account.company, 
                    account.balance, 
                    account.max_overdraft
                )

            # 转入发送提醒
            if operation == 0:
                self.send_recharge_success_notice(
                    account.company,
                    value,
                    account.balance
                )

            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)


    def get_records_by_company(self, company_id, start_date, end_date):
        objs = self.get_all_records().filter(
            cash_account__company__id = company_id,
            create_time__range=(start_date, end_date)
        )

        return objs


class SupplierBase(object):

    def get_all_supplier(self, state=None):
        objs = Supplier.objects.all()

        if state != None:
            objs = objs.filter(state=state)

        return objs

    def search_suppliers_for_admin(self, name):
        objs = self.get_all_supplier()

        if name:
            objs = objs.filter(name__contains=name)

        return objs

    def get_supplier_by_id(self, id):
        try:
            ps = dict(id=id)

            return Supplier.objects.get(**ps)
        except Supplier.DoesNotExist:
            return ""

    def add_supplier(self, name, contact, tel, addr, bank_name='', account_name='', \
            account_num='', sort=0, des='', remittance_des=''):

        if not (name and contact and tel and addr):
            return 99800, dict_err.get(99800)

        if Supplier.objects.filter(name=name):
            return 20801, dict_err.get(20801)

        try:
            obj = Supplier.objects.create(
                name = name,
                contact = contact,
                tel = tel,
                addr = addr,
                sort = sort,
                des = des,
                bank_name = bank_name,
                account_name = account_name,
                account_num = account_num,
                remittance_des = remittance_des
            )

            # 创建供货商对应的账户
            SupplierCashAccount.objects.create(supplier=obj)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

    def modify_supplier(self, supplier_id, name, contact, tel, addr, bank_name='', \
            account_name='', account_num='', state=1, sort=0, des='', remittance_des=''):

        if not (name and contact and tel and addr):
            return 99800, dict_err.get(99800)

        obj = self.get_supplier_by_id(supplier_id)
        if not obj:
            return 20802, dict_err.get(20802)

        if obj.name != name and Supplier.objects.filter(name=name):
            return 20801, dict_err.get(20801)

        try:
            obj.name = name
            obj.contact = contact
            obj.tel = tel
            obj.addr = addr
            obj.bank_name = bank_name
            obj.account_name = account_name
            obj.account_num = account_num
            obj.state = state
            obj.sort = sort
            obj.des = des
            obj.remittance_des = remittance_des
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_suppliers_by_name(self, name=""):
        objs = self.get_all_supplier()

        if name and name not in (".", u"。"):
            objs = objs.filter(name__contains=name)

        return objs[:10]


class SupplierCashAccountBase(object):

    def get_all_accounts(self):
        return SupplierCashAccount.objects.all()

    def get_accounts_for_admin(self, name):
        objs = self.get_all_accounts()

        if name:
            objs = objs.select_related('supplier').filter(supplier__name__contains=name)

        return objs

    def get_supplier_cash_account_by_id(self, account_id):
        try:
            return SupplierCashAccount.objects.select_related("supplier").get(id=account_id)
        except SupplierCashAccount.DoesNotExist:
            return ''

    def get_account_by_supplier(self, supplier_id):
        try:
            return SupplierCashAccount.objects.get(supplier_id=supplier_id)
        except SupplierCashAccount.DoesNotExist:
            return ''


class SupplierCashRecordBase(object):

    def get_all_records(self, operation=None):
        objs = SupplierCashRecord.objects.all()
        if operation:
            objs = objs.filter(operation=operation)

        return objs

    def get_records_for_admin(self, start_date, end_date, name, operation=None):
        objs = self.get_all_records(operation).filter(create_time__range=(start_date, end_date))

        if name:
            objs = objs.filter(cash_account__supplier__name__contains=name)

        return objs, objs.aggregate(Sum('value'))['value__sum']

    def validate_record_info(self, supplier_id, value, operation, notes):
        value = float(value)
        operation = int(operation)
        supplier = SupplierBase().get_supplier_by_id(supplier_id)
        assert operation in (0, 1)
        assert value > 0 and notes and supplier

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_cash_record_with_transaction(self, supplier_id, value, operation, notes, ip=None):
        try:
            errcode, errmsg = self.add_cash_record(supplier_id, value, operation, notes, ip)
            if errcode == 0:
                transaction.commit(using=DEFAULT_DB)
            else:
                transaction.rollback(using=DEFAULT_DB)
            return errcode, errmsg
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    def add_cash_record(self, supplier_id, value, operation, notes, ip=None):
        try:
            try:
                value = decimal.Decimal(value)
                operation = int(operation)
                self.validate_record_info(supplier_id, value, operation, notes)
            except Exception, e:
                return 99801, dict_err.get(99801)

            account, created = SupplierCashAccount.objects.get_or_create(supplier_id=supplier_id)

            if operation == 0:
                account.balance += value
            elif operation == 1:
                account.balance -= value
            account.save()

            SupplierCashRecord.objects.create(
                cash_account=account,
                value=value,
                current_balance=account.balance,
                operation=operation,
                notes=notes,
                ip=ip
            )

            return 0, dict_err.get(0)
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)


class PurchaseRecordBase(object):

    def get_all_records(self, state=None):
        objs = PurchaseRecord.objects.all()

        if state:
            objs = objs.filter(state=state)

        return objs

    def search_records_for_admin(self, name, state, start_date, end_date):
        objs = self.get_all_records(state).filter(
            create_time__range = (start_date, end_date)
        )

        if name:
            objs = objs.select_related('supplier').filter(
                supplier__name__contains=name
            )

        return objs, objs.aggregate(Sum('price'))['price__sum']

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_record(self, supplier_id, des, price, img, operator, ip):
        
        if not (supplier_id, des, price, operator):
            return 99800, dict_err.get(99800)

        obj = SupplierBase().get_supplier_by_id(supplier_id)
        if not obj:
            return 20802, dict_err.get(20802)

        try:
            assert price > 0

            record = PurchaseRecord.objects.create(
                supplier_id = supplier_id,
                des = des,
                price = price,
                img = img,
                operator = operator
            )
            
            errcode, errmsg = SupplierCashRecordBase().add_cash_record(
                supplier_id, price, 0, u'来自采购流水', ip
            )

            if errcode == 0:
                transaction.commit(using=DEFAULT_DB)
                return 0, record
            else:
                transaction.rollback(using=DEFAULT_DB)
                return errcode, errmsg

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)


    def get_record_by_id(self, record_id):
        try:
            return PurchaseRecord.objects.select_related("supplier").get(id=record_id)
        except PurchaseRecord.DoesNotExist:
            return ''

    @transaction.commit_manually(using=DEFAULT_DB)
    def modify_record(self, record_id, ip):

        if not record_id:
            return 99800, dict_err.get(99800)

        obj = self.get_record_by_id(record_id)
        if not obj:
            return 20901, dict_err.get(20901)

        try:
            obj.state = 0
            obj.save()
            
            errcode, errmsg = SupplierCashRecordBase().add_cash_record(
                obj.supplier_id, obj.price, 1, u'采购流水作废', ip
            )

            if errcode == 0:
                transaction.commit(using=DEFAULT_DB)
            else:
                transaction.rollback(using=DEFAULT_DB)
            return errcode, errmsg

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    def get_purchase_records(self, name, start_date, end_date):
        '''
        根据流水按供货商查询汇总信息
        '''
        return PurchaseRecord.objects.select_related('supplier').filter(
            state = 1,
            supplier__name__contains = name,
            create_time__range = (start_date, end_date)
        ).values('supplier_id').annotate(Sum('price'))


class SaleManBase(object):

    def get_all_sale_man(self, state=None):
        objs = SaleMan.objects.all()

        if state:
            objs = objs.filter(state=state)

        return objs

    def search_sale_man_for_admin(self, state=True):
        return self.get_all_sale_man(state)

    def add_sale_man(self, user_id, employee_date, state=True):
        
        user = UserBase().get_user_by_id(user_id)
        if not user:
            return 99800, dict_err.get(99800)

        try:
            obj = SaleMan.objects.create(
                user_id = user_id,
                employee_date = employee_date
            )
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

    def get_sale_man_by_id(self, sale_man_id):
        try:
            return SaleMan.objects.get(id=sale_man_id)
        except PurchaseRecord.DoesNotExist:
            return ''

    def modify_sale_man(self, sale_man_id, user_id, employee_date, state=True):
        
        if not (sale_man_id and user_id):
            return 99800, dict_err.get(99800)

        user = UserBase().get_user_by_id(user_id)
        if not user:
            return 99800, dict_err.get(99800)

        obj = self.get_sale_man_by_id(sale_man_id)
        if not obj:
            return 21001, dict_err.get(21001)

        try:
            obj.employee_date = employee_date
            obj.state = state
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj














