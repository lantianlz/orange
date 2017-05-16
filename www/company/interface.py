# -*- coding: utf-8 -*-

import datetime
import logging
import time
import random
import decimal
from django.db import transaction
from django.db.models import Sum, Count, Max
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache, raw_sql
from www.misc.decorators import cache_required
from www.misc import consts

from www.account.interface import UserBase, ExternalTokenBase
from models import Item, Company, Meal, MealItem, Order, OrderItem, \
    Booking, CompanyManager, CashAccount, CashRecord, Supplier, \
    SupplierCashAccount, SupplierCashRecord, PurchaseRecord, SaleMan, \
    InvoiceRecord, Invoice, RechargeOrder, Inventory, InventoryRecord, \
    InventoryToItem, ParttimePerson, ParttimeRecord

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
    20402: u'订单状态为非配送中，无法进行此操作',
    20403: u'订单状态为非准备中，无法进行此操作',

    20501: u'已预约，请勿重复提交',
    20502: u'没有找到对应的预约信息',

    20601: u'该管理员已存在，请勿重复添加',

    20701: u'没有找到对应的账户信息',
    20702: u'账户余额不足',

    20801: u'供货商名称重复',
    20801: u'没有找到对应的供货商',

    20901: u'没有找到对应的采购流水',

    21001: u'没有找到对应的销售人员',

    21101: u'没有找到对应的发票记录',

    21201: u'没有找到对应的发票',

    21301: u"没有找到对应的订单",
    21302: u"订单已支付",
    21303: u"付款金额和订单金额不符，支付失败，请联系客服人员",

    21401: u'没有找到对应的库存产品',

    21401: u'没有找到对应的库存产品对照信息',

    21501: u'没有找到对应的兼职人员信息',
    21502: u"同一天只能有一条记录",
}
dict_err.update(consts.G_DICT_ERROR)


class ItemBase(object):

    def generate_item_code(self, item_type):
        '''
        自动生成货号
        '''
        # 获得类别
        word = Item.code_dict[int(item_type)]

        last_code = 0

        # 查询此类别最后一个
        obj = Item.objects.filter(item_type=item_type).order_by('-code')
        if obj:
            last_code = obj[0].code
            last_code = int(last_code[1:])

        last_code = '%03d' % (last_code + 1)

        return word + last_code

    def get_all_item(self, state=[]):
        objs = Item.objects.all()

        if state != []:
            objs = objs.filter(state__in=state)

        return objs

    def add_item(self, name, item_type, spec, price, sort, integer, net_weight_rate, gross_profit_rate, init_add, supplier_id, des, img):

        if not (name and item_type and price and supplier_id and gross_profit_rate and net_weight_rate):
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
                net_weight_rate = net_weight_rate,
                gross_profit_rate=gross_profit_rate,
                init_add=init_add,
                supplier_id=supplier_id,
                des=des,
                img=img,
                code=self.generate_item_code(item_type)
            )
            item.sale_price = item.get_sale_price()
            item.save()

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, item

    def search_items_for_admin(self, item_type, state, supplier, name):
        objs = self.get_all_item(state)

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

    def modify_item(self, item_id, name, item_type, spec, price, sort,\
                    state, integer, net_weight_rate, gross_profit_rate, init_add, supplier_id, des, img):

        if not (name and item_type and price and supplier_id and gross_profit_rate and net_weight_rate):
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
            # 如果换了类别需要重新计算货号
            if obj.item_type != int(item_type):
                obj.code = self.generate_item_code(item_type)
                
            obj.name = name
            obj.item_type = item_type
            obj.spec = spec
            obj.price = price
            obj.sort = sort
            obj.state = state
            obj.integer = integer
            obj.init_add = init_add
            obj.net_weight_rate = net_weight_rate
            obj.gross_profit_rate = gross_profit_rate
            obj.sale_price = obj.get_sale_price()
            obj.supplier_id = supplier_id
            obj.des = des
            obj.img = img
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_items_by_name(self, name):
        objs = self.get_all_item([1, 2])

        if name:
            objs = objs.filter(name__contains=name)

        return objs

    def modify_fruit_price(self, item_id, price, net_weight_rate, flesh_rate, gross_profit_rate, wash_floating_rate):
        if not (item_id and price and net_weight_rate and flesh_rate and gross_profit_rate and wash_floating_rate):
            return 99800, dict_err.get(99800)
        
        obj = Item.objects.filter(id=item_id)
        if not obj:
            return 20102, dict_err.get(20102)
        obj = obj[0]
        try:
            obj.price = price
            obj.net_weight_rate = net_weight_rate
            obj.flesh_rate = flesh_rate
            obj.gross_profit_rate = gross_profit_rate
            obj.wash_floating_rate = wash_floating_rate
            obj.sale_price = obj.get_sale_price()
            obj.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_init_add_items(self):
        return self.get_all_item([1, 2]).filter(init_add=1)

    def get_items_by_type(self, item_type=1, state=[]):
        '''
        根据项目类型获取项目
        '''
        return self.get_all_item(state).filter(item_type=item_type)

    def get_top_used_items(self, item_type=1, days=180, top=20):
        '''
        获取历史订单中使用频率最高的项目
        item_type: 项目类型
        days: 时间长度
        top: 取前几
        '''
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)

        start_date = start_date.strftime('%Y-%m-%d') + ' 00:00:00'
        end_date = end_date.strftime('%Y-%m-%d') + ' 23:59:59'

        sql = """
            SELECT b.name, count(b.id) AS count, b.id 
            FROM company_orderitem a, company_item b, company_order c 
            WHERE a.item_id = b.id 
            AND b.item_type = %s
            AND b.state = 1
            AND c.id = a.order_id 
            AND c.state = 3 
            AND c.confirm_time > %s 
            AND c.confirm_time < %s 
            GROUP BY b.id 
            ORDER BY count DESC
            LIMIT 0, %s
        """
        
        return raw_sql.exec_sql(sql, [item_type, str(start_date), str(end_date), top])


class CompanyBase(object):

    def get_all_company(self, state=None):
        objs = Company.objects.all()

        if state != None:
            objs = objs.filter(state=state)

        return objs

    def search_companys_for_admin(self, name, short_name):
        objs = self.get_all_company()

        if name:
            objs = objs.filter(name__contains=name)

        if short_name:
            objs = objs.filter(short_name__contains=short_name)

        return objs

    def get_company_by_id(self, id):
        try:
            ps = dict(id=id)

            return Company.objects.get(**ps)
        except Company.DoesNotExist:
            return ""

    def add_company(self, name, staff_name, mobile, tel, addr, city_id, \
        sort, des, person_count, invite_by, is_show, logo, short_name, \
        sale_date, sale_by, longitude, latitude):

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
        else:
            sale_date = None

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
                longitude=longitude,
                latitude=latitude,
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
        is_show, logo, short_name, sale_date, sale_by, longitude, latitude):
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
        else:
            sale_date = None

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
            obj.longitude = longitude
            obj.latitude = latitude
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
        '''
        查询开放显示的公司
        '''

        return self.get_all_company(state=True).filter(is_show=1).order_by('-sort', 'id')

    def get_serviced_company_count(self):
        '''
        获取已经服务过的公司
        '''
        return Order.objects.select_related('company').filter(state=3).values('company__id').annotate(Count('company__id')).count() 


class MealBase(object):

    def _get_cycle_str(self, cycle):
        temp = []
        for x in range(1, 8):
            temp.append(str(x)) if str(x) in cycle else temp.append('0')
        
        return "-".join(temp)

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_meal(self, company_id, name, price, start_date, end_date, cycle, t_type, des='', meal_items=[]):
        if not (company_id and name and price and start_date and end_date and cycle):
            return 99800, dict_err.get(99800)

        if not CompanyBase().get_company_by_id(company_id):
            transaction.rollback(using=DEFAULT_DB)
            return 20202, dict_err.get(20202)

        try:

            # 套餐
            meal = Meal.objects.create(
                company_id=company_id,
                name=name,
                price=price,
                start_date=start_date,
                end_date=end_date,
                cycle='',
                t_type=t_type,
                des=des
            )
            # 非单次计算频次
            if t_type != "3":
                meal.cycle = self._get_cycle_str(cycle)
            else:
                meal.cycle = cycle[0]
            meal.save()

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
    def modify_meal(self, meal_id, company_id, name, price, start_date, end_date, state, cycle, t_type, des='', meal_items=[]):
        if not (company_id and name and price and start_date and end_date and cycle):
            return 99800, dict_err.get(99800)

        obj = self.get_meal_by_id(meal_id)
        if not obj:
            transaction.rollback(using=DEFAULT_DB)
            return 20302, dict_err.get(20302)

        if not CompanyBase().get_company_by_id(company_id):
            transaction.rollback(using=DEFAULT_DB)
            return 20202, dict_err.get(20202)

        if obj.name != name and Meal.objects.filter(name=name):
            transaction.rollback(using=DEFAULT_DB)
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
            # 非单次计算频次
            if t_type != "3":
                obj.cycle = self._get_cycle_str(cycle)
            else:
                obj.cycle = cycle[0]
            obj.t_type = t_type
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

    def search_meals_for_admin(self, state, name, cycle, t_type):
        objs = self.get_all_meal(state).filter(t_type__in=t_type)

        if name:
            objs = objs.filter(name__contains=name)

        if cycle:
            objs = objs.filter(cycle__contains=cycle)

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
    def add_order(self, meal_id, create_operator, total_price, order_items, person_count, owner, expected_time, is_test=False, note=''):

        if not (meal_id and create_operator and total_price and order_items and person_count and owner):
            return 99800, dict_err.get(99800)

        meal = MealBase().get_meal_by_id(meal_id)
        if not meal:
            transaction.rollback(using=DEFAULT_DB)
            return 20302, dict_err.get(20302)

        if not CompanyBase().get_company_by_id(meal.company_id):
            transaction.rollback(using=DEFAULT_DB)
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
                person_count=person_count,
                note=note,
                owner=owner,
                expected_time=expected_time
            )

            temp = decimal.Decimal(0)

            # 订单下的项目
            for x in order_items:

                item = ItemBase().get_item_by_id(x['item_id'])

                # 计算成本价
                temp += item.net_weight_price() * decimal.Decimal(x['amount'])

                OrderItem.objects.create(
                    order=obj,
                    item_id=x['item_id'],
                    amount=x['amount'],
                    price=item.net_weight_price(),
                    sale_price=item.get_sale_price(),
                    total_price=item.net_weight_price() * decimal.Decimal(x['amount']),
                    total_sale_price=item.get_sale_price() * decimal.Decimal(x['amount'])
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
    def modify_order(self, order_id, order_items, total_price, note, is_test, person_count, owner, expected_time=None):

        if not (order_id and total_price and order_items and person_count and owner):
            return 99800, dict_err.get(99800)

        obj = self.get_order_by_id(order_id)
        if not obj:
            transaction.rollback(using=DEFAULT_DB)
            return 20401, dict_err.get(20401)

        try:
            obj.total_price = total_price
            obj.note = note
            obj.is_test = is_test
            obj.person_count = person_count
            obj.owner = owner
            obj.expected_time = expected_time

            temp = decimal.Decimal(0)

            # 订单下的项目
            OrderItem.objects.filter(order=obj).delete()
            for x in order_items:

                item = ItemBase().get_item_by_id(x['item_id'])

                # 计算成本价
                temp += item.net_weight_price() * decimal.Decimal(x['amount'])

                OrderItem.objects.create(
                    order=obj,
                    item_id=x['item_id'],
                    amount=x['amount'],
                    price=item.net_weight_price(),
                    sale_price=item.get_sale_price(),
                    total_price=item.net_weight_price() * decimal.Decimal(x['amount']),
                    total_sale_price=item.get_sale_price() * decimal.Decimal(x['amount'])
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

    def search_orders_for_admin(self, start_date, end_date, state, company, is_test, owner=None, expected_time_sort=False):
        
        # 是否查询所有有效订单
        if state == -2:
            objs = Order.objects.filter(
                state__in=(1, 2, 3)
            )
        else:
            objs = self.get_all_order(state)

        if is_test:
            objs = objs.filter(is_test=True)

        if owner:
            user = UserBase().get_user_by_nick(owner)
            if user:
                objs = objs.filter(owner=user.id)

        objs = objs.select_related('company').filter(
            create_time__range=(start_date, end_date),
            company__name__contains=company
        )

        # 期望时间排序
        if expected_time_sort:
            objs = objs.order_by('expected_time')

        return objs, objs.aggregate(Sum('total_price'))['total_price__sum']

    def search_uncreate_orders_for_admin(self, start_date, end_date):
        # 查询出日期需要配送的套餐
        objs = MealBase().get_all_meal(state=1)
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
        except Order.DoesNotExist:
            return ""

    def get_order_by_order_no(self, order_no):
        try:
            ps = dict(order_no=order_no)

            return Order.objects.get(**ps)
        except Order.DoesNotExist:
            return ""

    def distribute_order(self, order_id, distribute_operator):
        '''
        配送订单
        '''
        obj = self.get_order_by_id(order_id)
        if not obj:
            return 20401, dict_err.get(20401)

        # 状态为准备中的订单才能配送
        if obj.state != 1:
            return 20403, dict_err.get(20403)

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
            transaction.rollback(using=DEFAULT_DB)
            return 20401, dict_err.get(20401)

        # 状态为配送中的订单才能确认完成
        if obj.state != 2:
            transaction.rollback(using=DEFAULT_DB)
            return 20402, dict_err.get(20402)

        try:
            obj.state = 3
            obj.confirm_operator = confirm_operator
            obj.confirm_time = datetime.datetime.now()
            obj.save()

            # 库存产品消耗
            code, msg = InventoryBase().calculate_inventory_cost_by_order(obj.id)
            
            if code != 0:
                transaction.rollback(using=DEFAULT_DB)
                return code, dict_err.get(code)
                
            # 试吃订单不操作账户
            if obj.is_test:
                transaction.commit(using=DEFAULT_DB)
            else:
                # 操作现金账户
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


    def search_orders_by_company(self, company_id, start_date, end_date, order_no, search_by_confirm_time=False):
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
            # 是否按确认时间查询
            if search_by_confirm_time:
                objs = objs.filter(confirm_time__range=(start_date, end_date))
            else:
                objs = objs.filter(create_time__range=(start_date, end_date))

        return objs, objs.aggregate(Sum('total_price'))['total_price__sum'] or 0

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
        return objs.aggregate(Sum('person_count'))['person_count__sum']

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
            AND d.name LIKE %s 
            AND a.confirm_time > %s 
            AND a.confirm_time < %s 
            GROUP BY c.supplier_id, a.order_no
        """
        
        return raw_sql.exec_sql(sql, ['%%%s%%' % name, str(start_date), str(end_date)])

    def get_latest_order_of_company(self, company_id):
        '''
        获取公司最近一次订单
        '''
        obj = None
        try:
            obj = Order.objects.filter(state=3, company=company_id).latest('id')
        except Exception, e:
            pass

        return obj

    def get_undone_orders_before_yesterdey(self):
        '''
        获取未完成的订单
        '''
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, yesterday.hour, yesterday.minute, yesterday.second)
        return Order.objects.filter(state__in=[1,2], create_time__lt=yesterday)

    def get_orders_by_date(self, start_date, end_date, state=3, is_test=False):
        
        return Order.objects.filter(
            state=state, 
            is_test=is_test,
            confirm_time__range=(start_date, end_date)
        )

    def modify_owner(self, order_id, owner):

        if not (order_id and owner):
            return 99800, dict_err.get(99800)

        order = OrderBase().get_order_by_id(order_id)
        if not order:
            return 21301, dict_err.get(21301)

        user = UserBase().get_user_by_id(owner)
        if not user:
            return 21001, dict_err.get(21001)

        try:
            order.owner = owner
            order.save()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)



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
            if invite:
                content = u'「%s」的「%s」收到「%s」的邀请，通过「%s」申请预订，联系电话「%s」' % (company_name, staff_name, invite.nick, sources.get(int(source), u'未知'), mobile)
            else:
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

        try:
            if isinstance(user, (str, unicode)):
                user = UserBase().get_user_by_id(user)

            cm = CompanyManager.objects.filter(company__id=company_id, user_id=user.id)

            return True if (cm or user.is_staff()) else False
        except Exception, e:
            return False

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

        return objs, objs.filter(balance__lt=0).aggregate(Sum('balance'))['balance__sum'] or 0

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

    def send_recharge_success_notice(self, company, amount, balance, pay_type=1):

        PAY_TYPE_DICT = {1: u'人工转账', 2: u'支付宝在线支付'}
        pay_type_str = PAY_TYPE_DICT.get(pay_type, u'人工转账')

        # 发送邮件提醒
        from www.tasks import async_send_email
        title = u'账户充值成功'
        content = u'账户「%s」通过「%s」成功充值「%.2f」元，当前余额「%.2f」元。' % (company.name, pay_type_str, amount, balance)
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

    def get_all_records(self, operation=None, is_invoice=None):
        objs = CashRecord.objects.all()
        if operation:
            objs = objs.filter(operation=operation)
        if is_invoice:
            objs = objs.filter(is_invoice=is_invoice)

        return objs

    def get_records_for_admin(self, start_date, end_date, name, operation=None, is_invoice=None, is_alipay=False):
        objs = self.get_all_records(operation, is_invoice).filter(create_time__range=(start_date, end_date))

        if name:
            objs = objs.filter(cash_account__company__name__contains=name)

        if operation == None and is_alipay:
            objs = objs.filter(operation=0, notes=u'支付宝在线充值')

        all_sum = 0
        # 如果没有指定操作类型
        if not operation:
            in_sum = objs.filter(operation=0).aggregate(Sum('value'))['value__sum']
            in_sum = in_sum or 0
            out_sum = objs.filter(operation=1).aggregate(Sum('value'))['value__sum']
            out_sum = out_sum or 0
            all_sum = in_sum - out_sum
        else:
            all_sum = objs.aggregate(Sum('value'))['value__sum']
            all_sum = all_sum or 0

        return objs, all_sum

    def validate_record_info(self, company_id, value, operation, notes):
        value = float(value)
        operation = int(operation)
        company = CompanyBase().get_company_by_id(company_id)
        assert operation in (0, 1)
        assert value > 0 and notes and company

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_cash_record_with_transaction(self, company_id, value, operation, notes, ip=None, is_invoice=1, pay_type=1):
        try:
            errcode, errmsg = self.add_cash_record(company_id, value, operation, notes, ip, is_invoice, pay_type)
            if errcode == 0:
                transaction.commit(using=DEFAULT_DB)
            else:
                transaction.rollback(using=DEFAULT_DB)
            return errcode, errmsg
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    def add_cash_record(self, company_id, value, operation, notes, ip=None, is_invoice=1, pay_type=1):
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
                ip=ip,
                is_invoice=is_invoice
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
                    account.balance,
                    pay_type
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

    def get_records_group_by_company(self, start_date, end_date, operation=None, is_invoice=None):
        '''
        根据公司分组获取现金流水记录

        '''
        objs = CashRecord.objects.filter(
            create_time__range=(start_date, end_date)
        )
        if operation is not None:
            objs = objs.filter(operation=operation)

        if is_invoice is not None:
            objs = objs.filter(is_invoice=is_invoice)

        return objs.values('cash_account__company_id').annotate(recharge=Sum('value'))

    def change_is_invoice(self, record_id):
        try:
            obj = CashRecord.objects.get(id = record_id)
            if obj.is_invoice == 1:
                obj.is_invoice = 0
            else:
                obj.is_invoice = 1

            obj.save()
            return 0, obj.is_invoice

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)


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

        return objs[:15]


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

        all_sum = 0
        # 如果没有指定操作类型
        if not operation:
            in_sum = objs.filter(operation=0).aggregate(Sum('value'))['value__sum']
            in_sum = in_sum or 0
            out_sum = objs.filter(operation=1).aggregate(Sum('value'))['value__sum']
            out_sum = out_sum or 0
            all_sum = in_sum - out_sum
        else:
            all_sum = objs.aggregate(Sum('value'))['value__sum']
            all_sum = all_sum or 0

        return objs, all_sum

    def validate_record_info(self, supplier_id, value, operation, notes):
        value = float(value)
        operation = int(operation)
        supplier = SupplierBase().get_supplier_by_id(supplier_id)
        assert operation in (0, 1)
        assert value > 0 and notes and supplier

    @transaction.commit_manually(using=DEFAULT_DB)
    def add_cash_record_with_transaction(self, supplier_id, value, operation, notes, ip=None, purchase_record_id=None):
        try:
            errcode, errmsg = self.add_cash_record(supplier_id, value, operation, notes, ip, purchase_record_id)
            if errcode == 0:
                transaction.commit(using=DEFAULT_DB)
            else:
                transaction.rollback(using=DEFAULT_DB)
            return errcode, errmsg
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)

    def add_cash_record(self, supplier_id, value, operation, notes, ip=None, purchase_record_id=None):
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
                ip=ip,
                purchase_record_id=purchase_record_id
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
        
        if not (supplier_id and des and price and operator):
            return 99800, dict_err.get(99800)

        obj = SupplierBase().get_supplier_by_id(supplier_id)
        if not obj:
            transaction.rollback(using=DEFAULT_DB)
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
                supplier_id, price, 0, u'来自采购流水', ip, record.id
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
            transaction.rollback(using=DEFAULT_DB)
            return 20901, dict_err.get(20901)

        try:
            obj.state = 0
            obj.save()
            
            errcode, errmsg = SupplierCashRecordBase().add_cash_record(
                obj.supplier_id, obj.price, 1, u'采购流水作废', ip, obj.id
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
        except SaleMan.DoesNotExist:
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


class StatisticsBase(object):

    def statistics_sale(self, start_date, end_date):
        '''
        销售统计
        '''

        return Meal.objects.select_related('company').filter(
            company__sale_date__range=(start_date, end_date),
            state = 1
        )


    @cache_required(cache_key='statistics_summary_data', expire=43200, cache_config=cache.CACHE_TMP)
    def statistics_summary(self):
        '''
        综合统计
        '''

        # 总服务公司数
        company_count = Order.objects.select_related('company').filter(state=3).values('company__id').annotate(Count('company__id')).count()

        # 总配送次数
        distribute_count = Order.objects.filter(state=3).count()

        # 总服务员工
        person_count = Company.objects.filter(state=1).aggregate(Sum('person_count'))['person_count__sum']

        # 总服务人次
        person_time_count = Order.objects.filter(state=3).aggregate(Sum('person_count'))['person_count__sum']

        # 总供货商数
        supplier_count = Supplier.objects.filter(state=1).count()

        # 配送水果总数
        fruit_count = OrderItem.objects.select_related('order', 'item').filter(order__state=3, item__item_type=1).aggregate(Sum('amount'))['amount__sum']

        # 配送点心总数
        cake_count = OrderItem.objects.select_related('order', 'item').filter(order__state=3, item__item_type=2).aggregate(Sum('amount'))['amount__sum']

        # 总销售额
        sale = Order.objects.filter(state=3, is_test=0).aggregate(Sum('total_price'))['total_price__sum']

        # 总原材料成本
        cost = Order.objects.filter(state=3, is_test=0).aggregate(Sum('cost_price'))['cost_price__sum']

        # 平均毛利率
        rate = round((1 - (cost / sale)) * 100, 1)

        # 根据订单汇总的总服务人次
        temp_person_time_count = Order.objects.filter(state=3, is_test=0).aggregate(Sum('person_count'))['person_count__sum']
        
        # 平均客单价
        per_customer_transaction = round(sale / temp_person_time_count, 1)

        # 统计时间
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return {
            'company_count': company_count,
            'distribute_count': distribute_count,
            'person_count': person_count,
            'person_time_count': person_time_count,
            'supplier_count': supplier_count,
            'fruit_count': fruit_count,
            'cake_count': cake_count,
            'sale': round(float(sale), 1),
            'cost': round(float(cost), 1),
            'rate': rate,
            'per_customer_transaction': per_customer_transaction,
            'date': date
        }

    def get_order_count_group_by_confirm_time(self, start_date, end_date):
        '''
        查询日订单数 按订单确认时间分组
        数据格式：
        [2014-01-01, 15], [2014-01-02, 23]
        '''
        sql = """
            SELECT DATE_FORMAT(confirm_time, "%%Y-%%m-%%d"), COUNT(id) 
            FROM company_order 
            WHERE %s <= confirm_time AND confirm_time <= %s
            AND state = 3
            GROUP BY DATE_FORMAT(confirm_time, "%%Y-%%m-%%d")
        """

        return raw_sql.exec_sql(sql, [start_date, end_date])

    def get_person_count_group_by_confirm_time(self, start_date, end_date):
        '''
        查询日服务人次数 按订单确认时间分组
        数据格式：
        [2014-01-01, 15], [2014-01-02, 23]
        '''
        sql = """
            SELECT DATE_FORMAT(a.confirm_time, "%%Y-%%m-%%d"), SUM(a.person_count)
            FROM company_order AS a, company_company AS b
            WHERE %s <= a.confirm_time AND a.confirm_time <= %s
            AND a.company_id = b.id
            AND a.state = 3
            GROUP BY DATE_FORMAT(a.confirm_time, "%%Y-%%m-%%d")
        """

        return raw_sql.exec_sql(sql, [start_date, end_date])

    def get_order_price_group_by_confirm_time(self, start_date, end_date):
        '''
        查询日订单总金额 按订单确认时间分组
        数据格式：
        [2014-01-01, 15], [2014-01-02, 23]
        '''
        sql = """
            SELECT DATE_FORMAT(confirm_time, "%%Y-%%m-%%d"), SUM(total_price) 
            FROM company_order 
            WHERE %s <= confirm_time AND confirm_time <= %s
            AND state = 3 AND is_test = 0
            GROUP BY DATE_FORMAT(confirm_time, "%%Y-%%m-%%d")
        """

        return raw_sql.exec_sql(sql, [start_date, end_date])

    def get_order_price_group_by_confirm_time_of_month(self, start_date, end_date):
        '''
        查询月订单总金额 按订单确认时间分组
        数据格式：
        [2014-01, 15], [2014-02, 23]
        '''
        sql = """
            SELECT DATE_FORMAT(confirm_time, "%%Y-%%m"), SUM(total_price) 
            FROM company_order 
            WHERE %s <= confirm_time AND confirm_time <= %s
            AND state = 3 AND is_test = 0
            GROUP BY DATE_FORMAT(confirm_time, "%%Y-%%m")
        """

        return raw_sql.exec_sql(sql, [start_date, end_date])

    def statistics_commission(self, start_date, end_date):
        '''
        '''
        return Meal.objects.select_related('company').filter(
            company__sale_date__range=(start_date, end_date),
            state=1,
            company__invite_by__isnull=False
        )

    def statistics_order_cost(self, start_date, end_date):

        # 总销售额
        sale = Order.objects.filter(
            state=3, 
            is_test=0,
            confirm_time__range=(start_date, end_date)
        ).aggregate(Sum('total_price'))['total_price__sum']
        sale = sale if sale else 0
        
        # 总订单成本
        cost = Order.objects.filter(
            state=3, 
            is_test=0,
            confirm_time__range=(start_date, end_date)
        ).aggregate(Sum('cost_price'))['cost_price__sum']
        cost = cost if cost else 0

        # 总试吃订单成本
        test_cost = Order.objects.filter(
            state=3, 
            is_test=1,
            confirm_time__range=(start_date, end_date)
        ).aggregate(Sum('cost_price'))['cost_price__sum']
        test_cost = test_cost if test_cost else 0

        # 总采购金额
        purchase = PurchaseRecordBase().get_all_records(True).filter(
            create_time__range = (start_date, end_date)
        ).aggregate(Sum('price'))['price__sum']
        purchase = purchase if purchase else 0

        # 总毛利
        gross_profit = sale - cost - test_cost

        # 订单成本与采购差额
        balance =  cost + test_cost - purchase

        return {
            'sale': str(sale),
            'cost': str(cost),
            'test_cost': str(test_cost),
            'gross_profit': str(gross_profit),
            'purchase': str(purchase),
            'balance': str(balance)
        }

    def statistics_percentage(self, start_date, end_date):
        '''
        提成统计
        查询月订单总金额,订单数 按归属人分组
        数据格式：
        ['归属人', 12345, 4], ['归属人', 12345, 4]
        '''
        sql = """
            SELECT owner, SUM(total_price) AS total, COUNT(owner)
            FROM company_order 
            WHERE %s <= confirm_time 
            AND confirm_time <= %s
            AND state = 3 AND is_test = 0
            AND owner <> ''
            GROUP BY owner
            ORDER BY total DESC
        """

        return raw_sql.exec_sql(sql, [start_date, end_date])

    def statistics_item_price(self, start_date, end_date, item_id):
        '''
        统计时间段产品价格
        ['2016-01-01', '8.8'], ['2016-01-02', '9.9']
        '''

        sql = """
            SELECT DATE_FORMAT(b.confirm_time, "%%Y-%%m-%%d"), a.price
            FROM company_orderitem a, company_order b
            WHERE a.item_id = %s
            AND a.order_id = b.id 
            AND b.state = 3
            AND %s <= b.confirm_time 
            AND b.confirm_time <= %s
        """

        return raw_sql.exec_sql(sql, [item_id, start_date, end_date])


class InvoiceRecordBase(object):

    def get_all_records(self, state=None):
        objs = InvoiceRecord.objects.all()

        if state:
            objs = objs.filter(state=state)

        return objs

    def search_records_for_admin(self, name, state, start_date, end_date):
        objs = self.get_all_records(state).filter(
            create_time__range = (start_date, end_date)
        )

        if name:
            objs = objs.select_related('company').filter(
                company__name__contains=name
            )

        return objs, objs.aggregate(Sum('invoice_amount'))['invoice_amount__sum']

    def get_record_by_id(self, record_id):
        try:
            return InvoiceRecord.objects.select_related("company").get(id=record_id)
        except InvoiceRecord.DoesNotExist:
            return ''

    def add_record(self, company_id, title, invoice_amount, content, invoice_date, operator, transporter=None, img=None):
        
        if not (company_id and title and invoice_amount and content and invoice_date and operator):
            return 99800, dict_err.get(99800)

        obj = CompanyBase().get_company_by_id(company_id)
        if not obj:
            return 20802, dict_err.get(20802)

        try:
            assert invoice_amount > 0

            record = InvoiceRecord.objects.create(
                company_id = company_id,
                title = title,
                invoice_amount = invoice_amount,
                content = content,
                invoice_date = invoice_date,
                operator = operator,
                transporter = transporter,
                img = img
            )

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, record

    def modify_record(self, record_id, company_id, title, invoice_amount, content, invoice_date, operator, state, transporter=None, img=None):
        
        if not (record_id and company_id and title and invoice_amount and content and invoice_date and operator):
            return 99800, dict_err.get(99800)
        
        company = CompanyBase().get_company_by_id(company_id)
        if not company:
            return 20802, dict_err.get(20802)

        obj = self.get_record_by_id(record_id)
        if not obj:
            return 21101, dict_err.get(21101)

        try:
            assert invoice_amount > 0

            obj.company_id = company_id
            obj.title = title
            obj.invoice_amount = invoice_amount
            obj.content = content
            obj.invoice_date = invoice_date
            obj.operator = operator
            obj.state = state
            obj.transporter = transporter
            obj.img = img
            obj.save()

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

    def get_invoice_amount_group_by_company(self, company_name, start_date, end_date):
        '''
        根据公司分组获取发票金额
        '''
        objs = InvoiceRecord.objects.filter(
            state__in=[1, 2],
            create_time__range=(start_date, end_date)
        )

        if company_name:
            objs = objs.filter(company__name__contains=company_name)

        return objs.values('company_id').annotate(invoice_amount=Sum('invoice_amount'))

    def get_latest_invoice_group_by_company(self, company_name, start_date, end_date):
        '''
        根据公司分组获取最后开票日期
        '''
        objs = InvoiceRecord.objects.filter(
            state__in=[1, 2],
            create_time__range=(start_date, end_date)
        )

        if company_name:
            objs = objs.filter(company__name__contains=company_name)

        return objs.values('company_id').annotate(invoice_date=Max('invoice_date'))

    def send_invoice_notice(self, companys):
        # 发送催发票提醒
        from www.tasks import async_send_email

        title = u"催款跟进"
        content = u"以下公司开票金额与充值金额不符，请及时跟进：\n%s" % (companys)

        async_send_email("vip@3-10.cc", title, content)
    
    def get_invoice_statement(self, company_name, start_date, end_date):
        '''
        发票对账
        '''

        data = {}

        # 发票金额数据
        invoice_record_data = self.get_invoice_amount_group_by_company(company_name, start_date, end_date)

        # 最后开票金额
        latest_invoice_data = self.get_latest_invoice_group_by_company(company_name, start_date, end_date)
        latest_invoice_dict = dict([[x['company_id'], x['invoice_date']] for x in latest_invoice_data])

        # 充值金额数据
        recharge_data = CashRecordBase().get_records_group_by_company(start_date, end_date, 0, 1)
        recharge_dict = {}
        for x in recharge_data:
            recharge_dict[x['cash_account__company_id']] = str(x['recharge'])

        # 公司数据
        company_data = CompanyBase().get_all_company(1).values('id', 'name', 'short_name')
        company_dict = {}
        for x in company_data:
            company_dict[x['id']] = [x['name'], '%s [ %s ]' % (x['name'], x['short_name'] or '-')]

        # 公司现金账户
        account_data = CashAccountBase().get_all_accounts().values('company_id', 'balance')
        account_dict = {}
        for x in account_data:
            account_dict[x['company_id']] = str(x['balance'])

        for x in invoice_record_data:
            key = x['company_id']
            data[key] = {
                'name': company_dict[key][0],
                'combine_name': company_dict[key][1],
                'account': account_dict.get(key, 0),
                'recharge': recharge_dict.get(key, 0),
                'invoice_amount': str(x['invoice_amount']),
                'offset_abs': round(abs(float(recharge_dict.get(key, 0)) - float(x['invoice_amount'])), 2),
                'offset': round(float(recharge_dict.get(key, 0)) - float(x['invoice_amount']), 2),
                'latest_date': str(latest_invoice_dict[key]),
                'need_notice': True if (datetime.datetime.now().date() - latest_invoice_dict[key]).days > 15 else False
            }

        data = data.values()
        # 排序 需要提醒的排列在前面
        data.sort(key=lambda x:x['offset_abs'], reverse=True)

        return data, sum([x['offset'] for x in data if x['offset'] < 0])

class InvoiceBase(object):
    
    def search_invoices_for_admin(self, name):
        objs = Invoice.objects.all()
        if name:
            objs = objs.filter(company__name__contains=name)

        return objs 

    def get_invoice_by_id(self, invoice_id):
        try:
            return Invoice.objects.select_related("company").get(id=invoice_id)
        except Invoice.DoesNotExist:
            return ''

    def get_invoice_by_company_id(self, company_id):
        try:
            return Invoice.objects.select_related("company").get(company_id=company_id)
        except Invoice.DoesNotExist:
            return ''

    def add_invoice(self, company_id, title, content):
        
        if not (company_id, title, content):
            return 99800, dict_err.get(99800)

        obj = CompanyBase().get_company_by_id(company_id)
        if not obj:
            return 20802, dict_err.get(20802)

        try:

            record = Invoice.objects.create(
                company_id = company_id,
                title = title,
                content = content
            )

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, record

    def modify_invoice(self, invoice_id, company_id, title, content):
        
        if not (invoice_id and company_id and title and content):
            return 99800, dict_err.get(99800)

        company = CompanyBase().get_company_by_id(company_id)
        if not company:
            return 20802, dict_err.get(20802)

        obj = self.get_invoice_by_id(invoice_id)
        if not obj:
            return 21201, dict_err.get(21201)

        try:

            obj.title = title
            obj.content = content
            obj.save()

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

class RechargeOrderBase(object):

    def generate_order_trade_id(self, pr):
        """
        @note: 生成订单的id，传入不同前缀来区分订单类型
        参数pr:
        1.充值 ====> CZ
        """
        postfix = '%s' % datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]  # 纯数字
        if pr:
            postfix = '%s%s%02d' % (pr, postfix, random.randint(0, 99))
        return postfix

    def get_order_by_trade_id(self, trade_id):
        obj = None
        try:
            obj = RechargeOrder.objects.get(trade_id=trade_id)
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
        return obj

    def create_order(self, company_id, total_fee, pay_type, ip):

        try:
            
            if not (company_id and total_fee and pay_type and ip):
                return 99800, dict_err.get(99800)
            
            try:
                total_fee = decimal.Decimal(total_fee)
                pay_type = int(pay_type)
                assert pay_type in (1,)
            except Exception, e:
                return 99801, dict_err.get(99801)

            obj = CompanyBase().get_company_by_id(company_id)
            if not obj:
                return 20202, dict_err.get(20202)

            order = RechargeOrder.objects.create(
                trade_id = self.generate_order_trade_id("CZ"),
                company_id = company_id,
                total_fee = total_fee,
                discount_fee = 0,
                pay_fee = total_fee,
                pay_type = pay_type
            )

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, order

    @transaction.commit_manually(using=DEFAULT_DB)
    def order_pay_callback(self, trade_id, payed_fee, pay_info):

        try:
            # 订单是否存在
            order = self.get_order_by_trade_id(trade_id)
            
            if not order:
                transaction.rollback(using=DEFAULT_DB)
                return 21301, dict_err.get(21301)

            # 订单是否已经支付
            if order.order_state == 1:
                transaction.rollback(using=DEFAULT_DB)
                return 21302, dict_err.get(21302)

            # 订单金额不符
            if order.pay_fee != decimal.Decimal(payed_fee):
                transaction.rollback(using=DEFAULT_DB)
                return 21303, dict_err.get(21303)

            # 添加充值流水
            flag, msg = CashRecordBase().add_cash_record(order.company_id, order.pay_fee, 0, u'支付宝在线充值', '', 1, 2)
            if flag != 0:
                transaction.rollback(using=DEFAULT_DB)
                return flag, msg

            order.payed_fee = payed_fee
            order.pay_info = pay_info
            order.pay_time = datetime.datetime.now()
            order.order_state = 1
            order.save()
            transaction.commit(using=DEFAULT_DB)
            return flag, msg

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)


class InventoryBase(object):
    '''
    库存产品
    '''
    
    def get_all_inventory(self, state):
        objs = Inventory.objects.all()

        if state != None:
            objs = objs.filter(state=state)

        return objs

    def search_inventorys_for_admin(self, name, state):
        objs = self.get_all_inventory(state)

        if name:
            objs = objs.filter(item__name__contains=name)

        return objs

    def get_inventorys_by_name(self, name):
        objs = self.get_all_inventory(True)
        if name:
            objs = objs.filter(item__name__contains=name)
        return objs

    def get_inventory_by_id(self, inventory_id):
        try:
            return Inventory.objects.get(id=inventory_id)
        except Inventory.DoesNotExist:
            return ''

    def add_inventory(self, item_id, amount=0, warning_value=0, state=1):

        if not item_id:
            return 99800, dict_err.get(99800)

        try:
            obj = Inventory.objects.create(
                item_id = item_id,
                amount = amount,
                warning_value = warning_value,
                state = state
            )
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

    def modify_inventory(self, inventory_id, amount=0, warning_value=0, state=1):

        if not inventory_id:
            return 99800, dict_err.get(99800)

        try:
            obj = self.get_inventory_by_id(inventory_id)
            if not obj:
                return 21401, dict_err.get(21401)

            obj.amount = amount
            obj.warning_value = warning_value
            obj.state = state
            obj.save()

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def send_inventory_notice(self, inventory):
        # 发送库存不足提醒
        from www.tasks import async_send_email

        title = u"库存不足"
        content = u"「%s」库存不足，当前余量：「%s」" % (inventory.item.name, inventory.amount)

        async_send_email("web@3-10.cc", title, content)

    def check_need_notice(self, inventory_id):
        '''
        '''
        try:
            obj = self.get_inventory_by_id(inventory_id)

            # 如果需要提醒
            if obj.amount <= obj.warning_value:
                self.send_inventory_notice(obj)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
    
    def calculate_inventory_cost_by_order(self, order_id):
        '''
        根据订单计算消耗产品
        '''

        order = OrderBase().get_order_by_id(order_id)

        # 查找出所有需要操作的库存产品
        # {'产品': [{'库存产品', '库存产品消耗数量'}]}
        inventory_cost_dict = {}
        inventory_dict = {}
        for x in self.get_all_inventory(True):
            key = str(x.item_id)
            inventory_dict[key] = [{'inventory_id': x.id, 'cost_count': 1}]
            inventory_cost_dict[x.id] = 0

        # 查找出产品与消耗库存产品的关系
        # {'产品': [{'库存产品', '库存产品消耗数量'}, {'库存产品', '库存产品消耗数量'}]}
        inventory_to_item_dict = {}
        for x in InventoryToItem.objects.all():
            key = str(x.item_id)

            if not inventory_to_item_dict.has_key(key):
                inventory_to_item_dict[key] = []
            inventory_to_item_dict[key].append({'inventory_id': x.inventory_id, 'cost_count': x.amount})

        # 合并
        inventory_dict.update(inventory_to_item_dict)

        # 根据订单来确认消耗的产品
        for order_item in OrderItem.objects.filter(order=order):
            key = str(order_item.item_id)
            temp = inventory_dict.get(key, None)

            if not temp:
                continue

            # 如果有消耗
            for x in temp:
                inventory_cost_dict[x['inventory_id']] += order_item.amount * x['cost_count']

        code = 0
        msg = ''
        # 循环扣除消耗
        for k, v in inventory_cost_dict.items():
            # 跳过值为0的
            if v == 0:
                continue

            code, msg = InventoryRecordBase().add_record(k, 1, v, order.confirm_operator, u"订单「%s」确认" % order.order_no)
            
            if code > 0:
                break

        return code, msg


class InventoryToItemBase(object):
    '''
    库存产品对照
    '''

    def search_relationship_for_admin(self, name):
        objs = InventoryToItem.objects.all()

        if name:
            objs = objs.filter(item__name__contains=name)

        return objs

    def get_relationship_by_id(self, relationship_id):
        try:
            return InventoryToItem.objects.get(id=relationship_id)
        except InventoryToItem.DoesNotExist:
            return ''

    def add_relationship(self, inventory_id, item_id, amount=0):
        '''
        添加对照关系
        '''

        if not (inventory_id and item_id):
            return 99800, dict_err.get(99800)

        try:
            obj = InventoryToItem.objects.create(
                inventory_id = inventory_id,
                item_id = item_id,
                amount = amount
            )
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj

    def drop_relationship(self, relationship_id):
        '''
        删除对照关系
        '''
        if not relationship_id:
            return 99800, dict_err.get(99800)

        try:
            obj = self.get_relationship_by_id(relationship_id)
            if not obj:
                return 21501, dict_err.get(21501)

            obj.delete()

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)


class InventoryRecordBase(object):

    def get_all_records(self, operation=None):
        objs = InventoryRecord.objects.all()

        if operation is not None:
            objs = objs.filter(operation=operation)

        return objs

    def search_records_for_admin(self, start_date, end_date, name, operation=None):
        objs = self.get_all_records(operation).filter(
            create_time__range = (start_date, end_date)
        )

        if name:
            objs = objs.select_related('inventory', 'item').filter(
                inventory__item__name__contains=name
            )

        return objs


    def add_record(self, inventory_id, operation, value, operator, notes):
        '''
        '''
        if not (inventory_id and operation and value and operator and notes):
            return 99800, dict_err.get(99800)

        # 检验参数
        try:
            value = int(value)
            operation = int(operation)
            assert value > 0
            assert operation in (0, 1)
        except Exception, e:
            return 99801, dict_err.get(99801)

        try:
            obj = InventoryRecord.objects.create(
                inventory_id = inventory_id,
                operation = operation,
                operator = operator,
                notes = notes,
                value = value
            )

            # 更新库存产品数量
            if operation == 0:
                obj.inventory.amount += value
            else:
                obj.inventory.amount -= value
            obj.inventory.save()
            # 更新记录表的余量
            obj.current_value = obj.inventory.amount
            obj.save()

            #是否需要提醒
            InventoryBase().check_need_notice(obj.inventory.id)

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, obj


    @transaction.commit_manually(using=DEFAULT_DB)
    def add_record_with_transaction(self, inventory_id, operation, value, operator, notes):
        '''
        '''
        try:
            errcode, errmsg = self.add_record(inventory_id, operation, value, operator, notes)
            
            if errcode == 0:
                transaction.commit(using=DEFAULT_DB)
            else:
                transaction.rollback(using=DEFAULT_DB)
            return errcode, errmsg
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            transaction.rollback(using=DEFAULT_DB)
            return 99900, dict_err.get(99900)


class ParttimePersonBase(object):

    '''
    兼职人员
    '''

    def search_person_for_admin(self, state, name):
        objs = ParttimePerson.objects.filter(state=state)

        if name:
            objs = objs.filter(name__contains=name)

        return objs

    def get_persons_by_name(self, name):
        objs = ParttimePerson.objects.all()

        if name:
            objs = objs.filter(name__contains=name)

        return objs

    def get_person_by_id(self, person_id):
        try:
            return ParttimePerson.objects.get(id=person_id)
        except ParttimePerson.DoesNotExist:
            return ''

    def get_person_by_name(self, person_name):
        try:
            return ParttimePerson.objects.get(name=person_name)
        except ParttimePerson.DoesNotExist:
            return ''

    def add_person(self, name, gender, age, tel, hourly_pay=10, state=1, note=''):
        
        if not (name, gender, age, tel, hourly_pay):
            return 99800, dict_err.get(99800)

        try:

            person = ParttimePerson.objects.create(
                name = name,
                gender = gender,
                age = age,
                tel = tel,
                hourly_pay = hourly_pay,
                note = note
            )

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, person

    def modify_person(self, person_id, name, gender, age, tel, hourly_pay=10, state=1, note=''):

        if not person_id:
            return 99800, dict_err.get(99800)

        if not (name, gender, age, tel, hourly_pay):
            return 99800, dict_err.get(99800)

        try:
            obj = self.get_person_by_id(person_id)
            if not obj:
                return 21501, dict_err.get(21501)

            obj.name = name
            obj.gender = gender
            obj.age = age
            obj.tel = tel
            obj.hourly_pay = hourly_pay
            obj.state = state
            obj.note = note
            obj.save()

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)


class ParttimeRecordBase(object):

    '''
    '''
    def search_records_for_admin(self, start_date, end_date, name):
        objs = ParttimeRecord.objects.filter(start_time__range=(start_date, end_date))

        if name:
            objs = objs.filter(person__name__contains=name)

        return objs, objs.aggregate(Sum('pay'))['pay__sum']


    def add_record(self, person_id, start_date, end_date, note):
        
        if not (person_id, start_date, end_date):
            return 99800, dict_err.get(99800)

        person = ParttimePersonBase().get_person_by_id(person_id)
        if not person:
            return 21501, dict_err.get(21501)

        try:
            s = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M') 
            e = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M')
            hour = round((e - s).seconds/60/60.0, 1)

            # 一个人一天只能有一条记录
            if ParttimeRecord.objects.filter(person_id=person_id, start_time__gt=start_date[:10] + " 00:00:00", start_time__lt=start_date[:10] + " 23:59:59"):
                return 21502, dict_err.get(21502)

            record = ParttimeRecord.objects.create(
                person_id = person_id,
                start_time = start_date,
                end_time = end_date,
                hour = hour,
                hourly_pay = person.hourly_pay,
                pay = round(hour * person.hourly_pay, 1),
                note = note
            )

        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, record


    def remove_record(self, record_id):

        if not (record_id):
            return 99800, dict_err.get(99800)

        try:
            ParttimeRecord.objects.filter(id=record_id).delete()
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)












