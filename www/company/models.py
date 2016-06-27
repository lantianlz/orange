# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
import datetime
import decimal

class Company(models.Model):

    '''
    @note: 公司
    '''
    state_choices = ((0, u"停用"), (1, u"正常"))
    show_choices = ((0, u"不显示"), (1, u"显示"))
    source_choices = ((0, u"地推"), (1, u""))

    name = models.CharField(verbose_name=u"名称", max_length=128, unique=True)
    short_name = models.CharField(verbose_name=u"简称", max_length=128, null=True)
    logo = models.CharField(verbose_name=u"logo", max_length=256, null=True)
    des = models.TextField(verbose_name=u"简介", null=True)
    staff_name = models.CharField(verbose_name=u"企业联系人", max_length=16, null=True)
    mobile = models.CharField(verbose_name=u"手机", max_length=32, null=True)
    tel = models.CharField(verbose_name=u"座机", max_length=32, null=True)
    addr = models.CharField(verbose_name=u"地址", max_length=256, null=True)
    person_count = models.IntegerField(verbose_name=u"员工总数", default=0)
    longitude = models.CharField(verbose_name=u"经度", max_length=32, null=True)
    latitude = models.CharField(verbose_name=u"纬度", max_length=32, null=True)
    invite_by = models.CharField(verbose_name=u"邀请人", max_length=32, null=True)
    city_id = models.IntegerField(verbose_name=u"所属城市", default=0)
    source = models.IntegerField(verbose_name=u"来源", default=0, choices=source_choices)
    state = models.IntegerField(verbose_name=u"状态", default=1, db_index=True, choices=state_choices)
    sort = models.IntegerField(verbose_name=u"排序", default=0)
    is_show = models.IntegerField(verbose_name=u"官网是否显示", default=1, choices=show_choices)
    sale_by = models.CharField(verbose_name=u"销售人", max_length=32, null=True)
    sale_date = models.DateTimeField(verbose_name=u"正式订购日期", null=True, db_index=True)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, db_index=True)

    def get_logo(self):
        return self.logo if self.logo else '%simg/logo.png' % settings.MEDIA_URL

    def combine_name(self):
        '''
        组合名字：
        成都乐动科技有点公司 [ 咕咚 ]
        '''
        return '%s [ %s ]' % (self.name, self.short_name or '-')

    class Meta:
        ordering = ["sort", "-create_time"]

class CompanyManager(models.Model):
    company = models.ForeignKey("Company")
    user_id = models.CharField(verbose_name=u"管理员id", max_length=32, db_index=True)
    role = models.IntegerField(verbose_name=u"角色", default=0, db_index=True)

    class Meta:
        unique_together = [("company", "user_id"), ]
        ordering = ["company"]

class CashAccount(models.Model):

    '''
    @note: 现金账户
    '''
    company = models.ForeignKey("Company", unique=True)
    balance = models.DecimalField(verbose_name=u"最新余额", max_digits=20, decimal_places=2, default=0, db_index=True)
    max_overdraft = models.DecimalField(verbose_name=u"最大透支额", max_digits=20, decimal_places=2, default=1000, db_index=True)

    class Meta:
        ordering = ['balance', 'id']

class CashRecord(models.Model):

    '''
    @note: 现金账户流水
    '''
    operation_choices = ((0, u"充值"), (1, u"消费"))

    cash_account = models.ForeignKey("CashAccount")
    value = models.DecimalField(verbose_name=u"操作金额", max_digits=20, decimal_places=2, db_index=True)
    current_balance = models.DecimalField(verbose_name=u"当时余额", max_digits=20, decimal_places=2, db_index=True)
    operation = models.IntegerField(verbose_name=u"操作类型", choices=operation_choices, db_index=True)
    notes = models.CharField(verbose_name=u"备注", max_length=256)
    is_invoice = models.IntegerField(verbose_name=u"是否记录开票金额", default=1, null=True, db_index=True)
    ip = models.CharField(verbose_name=u"ip", max_length=32, null=True)
    create_time = models.DateTimeField(verbose_name=u"流水时间", auto_now_add=True, db_index=True) 

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
    state_choices = ((0, u"停用"), (1, u"正常"), (2, u"正常,目录不显示"))
    type_choices = ((1, u"水果"), (2, u"点心"), (3, u"饮料"), (4, u"卤味"), (90, u"一次性耗材"), (91, u"盛装容器"), )
    spec_choices = ((1, u"斤"), (2, u"个"), (3, u"盒"), (4, u"袋"), (5, u"桶"), (6, u"杯"), (7, u"套"), (8, u"升"), (9, u"瓶"))
    integer_choices = ((1, u"整数"), (2, u"保留小数"))
    add_choices = ((1, u"添加"), (2, u"不添加"))

    code_dict = {1: 'F', 2: 'C', 3: 'D', 4: 'L', 90: 'S', 91: 'R'}

    code = models.CharField(verbose_name=u"货号", max_length=32, unique=True)
    name = models.CharField(verbose_name=u"名称", max_length=128, unique=True)
    item_type = models.IntegerField(verbose_name=u"类型", default=1, choices=type_choices)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices)
    spec = models.IntegerField(verbose_name=u"单位", default=1, choices=spec_choices)
    sort = models.IntegerField(verbose_name=u"排序", default=0)
    integer = models.IntegerField(verbose_name=u"是否整数", default=1, choices=integer_choices)
    init_add = models.IntegerField(verbose_name=u"是否默认添加", default=2, choices=add_choices)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    supplier = models.ForeignKey("Supplier")
    des = models.CharField(verbose_name=u"备注", max_length=256)
    img = models.CharField(verbose_name=u"图片", max_length=128, null=True)

    price = models.DecimalField(verbose_name=u"毛重成本价", max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField(verbose_name=u"售价", max_digits=10, decimal_places=2, default=0)
    net_weight_rate = models.DecimalField(verbose_name=u"净重比", max_digits=6, decimal_places=3, default=1)
    flesh_rate = models.DecimalField(verbose_name=u"果肉率", max_digits=6, decimal_places=3, default=1)
    gross_profit_rate = models.DecimalField(verbose_name=u"毛利率", max_digits=6, decimal_places=3, default=0.6)
    wash_floating_rate = models.DecimalField(verbose_name=u"洗切上浮比", max_digits=6, decimal_places=3, default=1.15)
    update_time = models.DateTimeField(verbose_name=u"最后更新时间", auto_now=True, db_index=True)

    def get_img(self):
        '''
        图片
        '''
        return self.img if self.img else '%simg/logo.png' % settings.MEDIA_URL

    def smart_des(self):
        if self.item_type != 1:
            return ('(%s)' % self.des) if self.des else ''
        else:
            return ''

    def smart_price(self):
        return round(self.price, 2)

    def net_weight_price(self):
        '''
        净重成本价格
        '''
        return decimal.Decimal(self.price) / decimal.Decimal(self.net_weight_rate)
    def smart_net_weight_price(self):
        return round(self.net_weight_price(), 2)

    def flesh_price(self):
        '''
        果肉成本价格
        '''
        return self.net_weight_price() / decimal.Decimal(self.flesh_rate)
    def smart_flesh_price(self):
        return round(self.flesh_price(), 2)

    def get_sale_price(self):
        '''
        获取卖价
        '''
        return self.net_weight_price() / (1 - decimal.Decimal(self.gross_profit_rate))
    def get_smart_sale_price(self):
        return round(self.get_sale_price(), 2)

    def wash_floating_price(self):
        '''
        洗切后价格
        '''
        return self.get_sale_price() * decimal.Decimal(self.wash_floating_rate)
    def smart_wash_floating_price(self):
        return round(self.wash_floating_price(), 2)

    def last_update_days(self):
        '''
        距离上次更新时间
        '''
        return (datetime.datetime.now() - self.update_time).days

    class Meta:
        ordering = ["sort", "-create_time"]


class Meal(models.Model):

    '''
    @note: 套餐
    '''
    state_choices = ((0, u"停用"), (1, u"正常"))
    type_choices = ((1, u"每周"), (2, u"隔周"), (3, u"单次"))

    company = models.ForeignKey("Company")
    name = models.CharField(verbose_name=u"名称", max_length=128, db_index=True)
    des = models.TextField(verbose_name=u"描述", null=True)
    price = models.DecimalField(verbose_name=u"价格", max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField(verbose_name=u"开始日期", db_index=True)
    end_date = models.DateField(verbose_name=u"结束日期", db_index=True)
    cycle = models.CharField(verbose_name=u"配送频率", max_length=32, null=True)
    t_type = models.IntegerField(verbose_name=u"配送类型", default=1, choices=type_choices)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, db_index=True)

    def get_cycle_str(self):

        if not self.cycle:
            return ""

        temp = []
        dict_map = [u'一', u'二', u'三', u'四', u'五', u'六', u'日']
        for x in self.cycle.split('-'):
            if x != '0':
                temp.append(dict_map[int(x)-1])
            else:
                temp.append(u"  ")

        return "-".join(temp)

    def get_expect_price_per_month(self, start_date, end_date, sale_date):
        '''
        计算每月的预期销售额
        '''
        expect_price = 0

        # 每周
        if self.t_type == 1:
            cycle = self.cycle or "0-0-0-0-0-0-0"
            temp = cycle.split('-')
            count = len(temp) - temp.count('0')
            expect_price = self.price * 4 * count

        # 隔周
        if self.t_type == 2:
            cycle = self.cycle or "0-0-0-0-0-0-0"
            temp = cycle.split('-')
            count = len(temp) - temp.count('0')
            expect_price = self.price * 2 * count

        # 单次
        if self.t_type == 3:
            # import datetime
            # today = datetime.datetime.now()
            # 如果在查询的时间段
            if (start_date <= sale_date) and (sale_date < end_date):
                expect_price = self.price

        return expect_price

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
    person_count = models.IntegerField(verbose_name=u"员工总数", default=0)
    is_test = models.BooleanField(verbose_name=u"是否试吃", default=False)
    cost_price = models.DecimalField(verbose_name=u"成本价", max_digits=10, decimal_places=2, default=0)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices, db_index=True)

    # 毛利
    def rate(self):
        return round((1 - (self.cost_price / self.total_price)) * 100, 2) if self.total_price else 0

    class Meta:
        ordering = ["-create_time"]

class OrderItem(models.Model):

    '''
    @note: 每日订单下的项目
    '''
    order = models.ForeignKey("Order")
    item = models.ForeignKey("Item")
    amount = models.FloatField(verbose_name=u"数量", default=0)
    price = models.DecimalField(verbose_name=u"成本价", max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField(verbose_name=u"售价", max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(verbose_name=u"成本总价", max_digits=10, decimal_places=2, default=0)
    total_sale_price = models.DecimalField(verbose_name=u"销售总价", max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = [("order", "item"), ]


class Invoice(models.Model):
    '''
    @note: 发票
    '''
    invoice_type_choices = ((1, u"增值税普通发票"),)

    company = models.ForeignKey("Company", unique=True)
    title = models.CharField(verbose_name=u"发票抬头", max_length=128)
    content = models.CharField(verbose_name=u"发票内容", max_length=256)
    invoice_type = models.IntegerField(verbose_name=u"发票类型", default=1, choices=invoice_type_choices)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ["-create_time"]

class InvoiceRecord(models.Model):
    '''
    @note: 发票记录
    '''
    state_choices = ((1, u"未打款"), (2, u"已打款"), (9, u"已作废"))

    company = models.ForeignKey("Company")
    title = models.CharField(verbose_name=u"发票抬头", max_length=128)
    invoice_amount = models.DecimalField(verbose_name=u"发票金额", max_digits=10, decimal_places=2, default=0)
    content = models.CharField(verbose_name=u"发票内容", max_length=256)
    transporter = models.CharField(verbose_name=u"配送人", max_length=32, null=True)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices)
    invoice_date = models.DateField(verbose_name=u"开票日期")
    img = models.CharField(verbose_name=u"图片", max_length=128, null=True)
    operator = models.CharField(verbose_name=u"操作人", max_length=32)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-invoice_date", "-create_time"]

class Supplier(models.Model):
    '''
    供货商
    '''
    state_choices = ((0, u"停用"), (1, u"正常"))

    name = models.CharField(verbose_name=u"名称", max_length=128, unique=True)
    contact = models.CharField(verbose_name=u"联系人", max_length=128)
    tel = models.CharField(verbose_name=u"电话", max_length=32)
    des = models.TextField(verbose_name=u"简介", null=True)
    addr = models.CharField(verbose_name=u"地址", max_length=256, null=True)
    bank_name = models.CharField(verbose_name=u"开户银行名称", max_length=128, null=True)
    account_name = models.CharField(verbose_name=u"银行户名", max_length=128, null=True)
    account_num = models.CharField(verbose_name=u"银行账号", max_length=128, null=True)
    remittance_des = models.TextField(verbose_name=u"打款备注", null=True)
    img = models.CharField(verbose_name=u"图片", max_length=128, null=True)
    state = models.IntegerField(verbose_name=u"状态", default=1, db_index=True, choices=state_choices)
    sort = models.IntegerField(verbose_name=u"排序", default=0)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["sort", "-create_time"]

class SupplierCashAccount(models.Model):

    '''
    @note: 供货商现金账户
    '''
    supplier = models.ForeignKey("Supplier", unique=True)
    balance = models.DecimalField(verbose_name=u"最新余额", max_digits=20, decimal_places=2, default=0, db_index=True)

    class Meta:
        ordering = ['-balance', 'id']

class SupplierCashRecord(models.Model):

    '''
    @note: 供货商现金账户流水
    '''
    operation_choices = ((0, u"入账"), (1, u"转出"))

    cash_account = models.ForeignKey("SupplierCashAccount")
    value = models.DecimalField(verbose_name=u"操作金额", max_digits=20, decimal_places=2, db_index=True)
    current_balance = models.DecimalField(verbose_name=u"当时余额", max_digits=20, decimal_places=2, db_index=True)
    operation = models.IntegerField(verbose_name=u"操作类型", choices=operation_choices, db_index=True)
    notes = models.CharField(verbose_name=u"备注", max_length=256)
    ip = models.CharField(verbose_name=u"ip", max_length=32, null=True)
    purchase_record_id = models.CharField(verbose_name=u"采购流水id", max_length=32, null=True)
    create_time = models.DateTimeField(verbose_name=u"流水时间", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-id']

class PurchaseRecord(models.Model):

    '''
    采购流水
    '''
    state_choices = ((0, u"作废"), (1, u"正常"))

    supplier = models.ForeignKey("Supplier")
    des = models.TextField(verbose_name=u"简介", null=True)
    price = models.DecimalField(verbose_name=u"采购价格", max_digits=10, decimal_places=2, default=0)
    operator = models.CharField(verbose_name=u"操作人", max_length=128)
    create_time = models.DateTimeField(verbose_name=u"流水时间", auto_now_add=True, db_index=True)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices, db_index=True)
    img = models.CharField(verbose_name=u"流水图片", max_length=128, null=True)

    class Meta:
        ordering = ["-create_time"]


class SaleMan(models.Model):

    '''
    销售人员表
    '''
    state_choices = ((0, u"无效"), (1, u"有效"))

    user_id = models.CharField(verbose_name=u"用户id", max_length=32, db_index=True, unique=True)
    employee_date = models.DateTimeField(verbose_name=u"入职时间", null=True)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices)

    class Meta:
        ordering = ["-id"]



class Inventory(models.Model):

    '''
    库存表
    '''
    state_choices = ((0, u"无效"), (1, u"有效"))

    item = models.ForeignKey("Item", unique=True)
    amount = models.IntegerField(verbose_name=u"库存数量", default=0)
    warning_value = models.IntegerField(verbose_name=u"预警值", default=0)
    state = models.IntegerField(verbose_name=u"状态", default=1, choices=state_choices)
    create_time = models.DateTimeField(verbose_name=u"创建时间", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-id"]


class InventoryRecord(models.Model):
    
    '''
    库存出入库记录表
    '''
    operation_choices = ((0, u"入库"), (1, u"出库"))

    inventory = models.ForeignKey("Inventory")
    operation = models.IntegerField(verbose_name=u"操作类型", choices=operation_choices, db_index=True)
    operator = models.CharField(verbose_name=u"操作人", max_length=128)
    create_time = models.DateTimeField(verbose_name=u"操作时间", auto_now_add=True, db_index=True)
    notes = models.CharField(verbose_name=u"备注", max_length=256)
    value = models.IntegerField(verbose_name=u"操作数量", default=0)
    current_value = models.IntegerField(verbose_name=u"当时余量", default=0)

    class Meta:
        ordering = ['-id']


class InventoryToItem(models.Model):

    '''
    库存与项目对照表
    '''
    
    inventory = models.ForeignKey('Inventory')
    item = models.ForeignKey('Item')
    amount = models.IntegerField(verbose_name=u"数量", default=0)
    create_time = models.DateTimeField(verbose_name=u"操作时间", auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [("inventory", "item"), ]
        ordering = ['-id']


class ParttimePerson(models.Model):

    '''
    兼职人员表
    '''

    gender_choices = ((0, u"女"), (1, u"男"))
    state_choices = ((0, u"无效"), (1, u"正常"))

    name = models.CharField(verbose_name=u"姓名", max_length=32)
    gender = models.IntegerField(verbose_name=u"性别", choices=gender_choices, default=1)
    age = models.IntegerField(verbose_name=u"年龄", default=18)
    tel = models.CharField(verbose_name=u"联系电话", max_length=32)
    hourly_pay = models.FloatField(verbose_name=u"时薪", default=10)
    state = models.IntegerField(verbose_name=u"状态", choices=state_choices, default=1)
    note = models.CharField(verbose_name=u"备注", max_length=256, null=True, default='')
    create_time = models.DateTimeField(verbose_name=u"操作时间", auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [("name", "tel"), ]
        ordering = ['-id']


class ParttimeRecord(models.Model):

    '''
    兼职工作记录表
    '''

    person = models.ForeignKey('ParttimePerson')
    start_time = models.DateTimeField(verbose_name=u"开始时间")
    end_time = models.DateTimeField(verbose_name=u"结束时间")
    hour = models.FloatField(verbose_name=u"工作时长")
    hourly_pay = models.FloatField(verbose_name=u"时薪")
    pay = models.FloatField(verbose_name=u"结算金额")
    note = models.CharField(verbose_name=u"备注", max_length=256, null=True)
    create_time = models.DateTimeField(verbose_name=u"操作时间", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-id']




