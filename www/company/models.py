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
    city_id = models.IntegerField(default=0)
    person_count = models.IntegerField(default=0)
    source = models.IntegerField(default=0, choices=source_choices)

    state = models.BooleanField(default=True, db_index=True)


class CashAccount(models.Model):

    '''
    @note: 现金账户
    '''
    # 透支额度、账户余额


class CashRecord(models.Model):

    '''
    @note: 现金账户流水
    '''


class Meal(models.Model):

    '''
    @note: 套餐
    '''

    price = models.FloatField()
    person_count = models.IntegerField()


class Order(models.Model):

    '''
    @note: 订单
    '''
    # 订单状态，试吃订单


class Invoice(models.Model):

    '''
    @note: 发票
    '''
    # 发票状态
