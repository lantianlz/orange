# -*- coding: utf-8 -*-

from django.db import models


class Company(models.Model):

    '''
    @note: 公司
    '''

    name = models.CharField(max_length=128, unique=True)
    logo = models.CharField(max_length=256, null=True)
    des = models.TextField(null=True)
    person_count = models.IntegerField(default=0)

    state = models.BooleanField(default=True, db_index=True)


class Meal(models.Model):

    '''
    @note: 套餐
    '''

    price = models.FloatField()
    person_count = models.IntegerField()


class Order(models.Model):

    '''
    @note: 套餐
    '''
