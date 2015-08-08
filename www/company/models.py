# -*- coding: utf-8 -*-

from django.db import models


class Company(models.Model):

    '''
    @note: 公司
    '''
    state_choices = ((0, u"停用"), (1, u"正常"))
    source_choices = ((0, u"地推"), (1, u""))

    name = models.CharField(verbose_name=u"名称", max_length=128, unique=True)
    logo = models.CharField(verbose_name=u"logo", max_length=256, null=True)
    des = models.TextField(verbose_name=u"简介", null=True)
    staff_name = models.CharField(verbose_name=u"企业联系人", max_length=16, null=True)
    mobile = models.CharField(verbose_name=u"手机", max_length=32, null=True)
    tel = models.CharField(verbose_name=u"座机", max_length=32, null=True)
    addr = models.CharField(verbose_name=u"地址", max_length=256, null=True)
    person_count = models.IntegerField(verbose_name=u"员工总数", default=0)
    invite_by = models.CharField(verbose_name=u"邀请人", max_length=32, null=True)

    city_id = models.IntegerField(verbose_name=u"所属城市", default=0)
    source = models.IntegerField(verbose_name=u"来源", default=0, choices=source_choices)
    state = models.IntegerField(verbose_name=u"状态", default=1, db_index=True, choices=state_choices)
    sort = models.IntegerField(verbose_name=u"排序", default=0)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, db_index=True)


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


class Booking(models.Model):

    '''
    @note: 企业预留预订信息
    '''
    state_choices = ((0, u"未处理"), (1, u"已处理"))
    source_choices = ((0, u"官网"), (1, u"微信"), (2, u"IT桔子"), (3, u"拉勾网"))

    company_name = models.CharField(verbose_name=u"公司名称", max_length=64)
    staff_name = models.CharField(verbose_name=u"企业联系人", max_length=16)
    mobile = models.CharField(verbose_name=u"企业联系人电话", max_length=32)
    source = models.IntegerField(verbose_name=u"来源", default=0, choices=source_choices)
    invite_by = models.CharField(verbose_name=u"邀请人", max_length=32, null=True)
    state = models.IntegerField(verbose_name=u"状态", default=0, choices=state_choices, db_index=True)
    operator_id = models.CharField(verbose_name=u"处理人", max_length=32, null=True)
    operation_time = models.DateTimeField(verbose_name=u"处理时间", null=True)
    note = models.CharField(verbose_name=u"备注", max_length=512, null=True)
    create_time = models.DateTimeField(verbose_name=u"预约时间", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-create_time"]

class Item(models.Model):

    '''
    @note: 单项
    '''
    state_choices = ((0, u"停用"), (1, u"正常"))
    type_choices = ((1, u"水果"), (2, u"点心"), (3, u"一次性耗材"), (4, u"盛装容器"))
    code_dict = {1: 'F', 2: 'C', 3: 'S', 4: 'R'}

    code = models.CharField(verbose_name=u"货号", max_length=32, unique=True)
    name = models.CharField(verbose_name=u"名称", max_length=128, unique=True)
    price = models.DecimalField(verbose_name=u"单价", max_digits=10, decimal_places=2, default=0)
    item_type = models.IntegerField(verbose_name=u"类型", default=1, choices=type_choices)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices)
    spec = models.CharField(verbose_name=u"规格", max_length=32, null=True)
    sort = models.IntegerField(verbose_name=u"排序", default=0, choices=type_choices)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)

    img = models.CharField(verbose_name=u"图片", max_length=128, null=True)

    class Meta:
        ordering = ["sort", "-create_time"]


class Meal(models.Model):

    '''
    @note: 套餐
    '''
    state_choices = ((0, u"停用"), (1, u"正常"))

    company = models.ForeignKey("Company")
    name = models.CharField(verbose_name=u"名称", max_length=128, db_index=True)
    des = models.TextField(verbose_name=u"描述", null=True)
    price = models.DecimalField(verbose_name=u"价格", max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField(verbose_name=u"开始日期", db_index=True)
    end_date = models.DateField(verbose_name=u"结束日期", db_index=True)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-create_time"]

class MealItem(models.Model):

    '''
    @note: 套餐下的项目
    '''
    meal = models.ForeignKey("Meal")
    item = models.ForeignKey("Item")
    amount = models.FloatField(verbose_name=u"数量", default=0)

    class Meta:
        unique_together = [("meal", "item"), ]


class Order(models.Model):

    '''
    @note: 每日订单
    '''
    state_choices = ((0, u"作废"), (1, u"准备中"), (2, u"配送中"), (3, u"已完成"))

    meal = models.ForeignKey("Meal")
    company = models.ForeignKey("Company")
    order_no = models.CharField(verbose_name=u"订单号", max_length=32, db_index=True)
    create_operator = models.CharField(verbose_name=u"订单创建人", max_length=32)
    create_time = models.DateTimeField(verbose_name=u"订单创建时间", auto_now_add=True, db_index=True)
    distribute_operator = models.CharField(verbose_name=u"订单配送人", max_length=32, null=True)
    distribute_time = models.DateTimeField(verbose_name=u"订单配送时间", null=True)
    confirm_operator = models.CharField(verbose_name=u"订单确认人", max_length=32, null=True)
    confirm_time = models.DateTimeField(verbose_name=u"订单确认时间", null=True)
    total_price = models.DecimalField(verbose_name=u"订单价格", max_digits=10, decimal_places=2, default=0)
    note = models.TextField(verbose_name=u"备注", null=True)
    is_test = models.BooleanField(verbose_name=u"是否试吃", default=False)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices, db_index=True)

    class Meta:
        ordering = ["-create_time"]

class OrderItem(models.Model):

    '''
    @note: 每日订单下的项目
    '''
    order = models.ForeignKey("Order")
    item = models.ForeignKey("Item")
    amount = models.FloatField(verbose_name=u"数量", default=0)
    price = models.DecimalField(verbose_name=u"单价", max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(verbose_name=u"总价", max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = [("order", "item"), ]

class Invoice(models.Model):

    '''
    @note: 发票
    '''
    customer_type_choices = ((0, u"个人"), (1, u"企业"))
    taxpayer_type_choices = ((0, u"增值税普通发票"), (1, u"增值税专用发票"))

    company = models.ForeignKey("Company")
    un_invoice_amount = models.DecimalField(verbose_name=u"未开发票金额", max_digits=10, decimal_places=2, default=0)
    title = models.CharField(verbose_name=u"发票抬头", max_length=32)
    customer_type = models.IntegerField(verbose_name=u"开具类型", default=0, choices=customer_type_choices)
    taxpayer_type = models.IntegerField(verbose_name=u"发票类型", default=0, choices=taxpayer_type_choices)


class InvoiceRecord(models.Model):

    invoice = models.ForeignKey("Invoice")
    invoice_amount = models.DecimalField(verbose_name=u"发票金额", max_digits=10, decimal_places=2, default=0)
    operator = models.CharField(verbose_name=u"开票人", max_length=32)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, db_index=True)
