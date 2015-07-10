# -*- coding: utf-8 -*-

from django.db import models


class Company(models.Model):

    '''
    @note: 公司
    '''

    source_choices = ((0, u"地推"), (1, u""))

    name = models.CharField(max_length=128, unique=True)
    logo = models.CharField(max_length=256, null=True)
    des = models.TextField(null=True)
    staff_name = models.CharField(max_length=16, null=True)     # 企业联系人
    mobile = models.CharField(max_length=32, null=True)
    tel = models.CharField(max_length=32, null=True)
    addr = models.CharField(max_length=256, null=True)

    city_id = models.IntegerField(default=0)
    person_count = models.IntegerField(default=0)
    source = models.IntegerField(default=0, choices=source_choices)
    state = models.BooleanField(default=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)


class CashAccount(models.Model):

    '''
    @note: 现金账户
    '''
    company = models.ForeignKey("Company", unique=True)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0, db_index=True)    # 最新余额
    max_overdraft = models.DecimalField(max_digits=20, decimal_places=2, default=0, db_index=True)  # 最大透支额


class CashRecord(models.Model):

    '''
    @note: 现金账户流水
    '''
    operation_choices = ((0, u"转入"), (1, u"转出"))

    cash_account = models.ForeignKey("CashAccount")
    value = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    current_balance = models.DecimalField(max_digits=20, decimal_places=2, db_index=True)
    operation = models.IntegerField(choices=operation_choices, db_index=True)  # 转入or转出
    notes = models.CharField(max_length=256)    # 流水介绍
    ip = models.CharField(max_length=32, null=True)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)  # 创建时间

    class Meta:
        ordering = ['-id']


class RechargeOrder(models.Model):

    """
    @note: 充值订单
    """
    pay_type_choices = ((0, u'零支付'), (1, u'支付宝'), (2, u'微信'), (3, u"企业账户转账"))
    order_state_choices = ((0, u'未付款'), (1, u'已付款'), )

    trade_id = models.CharField(max_length=32, db_index=True, unique=True)  # 非自增id,可以修改
    company = models.ForeignKey("Company")

    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 总的结算金额
    discount_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 优惠金额
    pay_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 应付金额   最终需要用户支付金额
    pay_type = models.IntegerField(default=0, choices=pay_type_choices, db_index=True)  # 支付方式

    payed_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 支付接口回调反馈的实际付款金额
    pay_time = models.DateTimeField(null=True, blank=True)  # 支付接口回调的时间
    pay_info = models.CharField(max_length=256, null=True, blank=True)  # 用户支付成功后保存支付信息
    order_state = models.IntegerField(default=0, choices=order_state_choices, db_index=True)  # 订单状态,默认为未确认状态
    is_admin_modify_pay_fee = models.BooleanField(default=False)  # 管理员是否修改应付金额
    ip = models.IPAddressField(null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-id', ]


class BookInfo(models.Model):

    '''
    @note: 企业预留预订信息
    '''
    state_choices = ((0, u"未处理"), (1, u"已处理"))
    source_choices = ((0, u"官网"), (1, u"IT桔子"), (1, u"拉勾网"), (1, u"推事本"), )

    company_name = models.CharField(max_length=64)
    staff_name = models.CharField(max_length=16)     # 企业联系人
    mobile = models.CharField(max_length=32)
    source = models.IntegerField(default=0, choices=source_choices)

    state = models.IntegerField(default=0, choices=state_choices)
    operation_user_id = models.IntegerField(null=True)
    note = models.CharField(max_length=512)


class Meal(models.Model):

    '''
    @note: 套餐
    '''

    name = models.CharField(max_length=128, unique=True)
    des = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class MealOrder(models.Model):

    '''
    @note: 订单
    '''
    # 订单状态，试吃订单


class Invoice(models.Model):

    '''
    @note: 发票
    '''
    # 发票状态


class InvoiceMealOrder(models.Model):

    '''
    @note: 发票对应的订单
    '''
    # 发票状态
