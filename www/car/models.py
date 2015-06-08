# -*- coding: utf-8 -*-

from django.db import models


class Brand(models.Model):

    '''
    @note: 品牌
    '''

    name = models.CharField(max_length=128, db_index=True)
    first_word = models.CharField(max_length=4, db_index=True)
    ex_id = models.IntegerField()
    des = models.TextField(null=True)
    img = models.CharField(max_length=256, null=True)
    parent_brand = models.ForeignKey("Brand", null=True, db_index=True)
    state = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = [("name", "parent_brand"), ]


class Serial(models.Model):

    '''
    @note: 系列
    '''

    name = models.CharField(max_length=128)
    brand = models.ForeignKey("Brand")
    ex_id = models.IntegerField()
    img = models.CharField(max_length=256, null=True)
    state = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = [("name", "brand"), ]


class CarBasicInfo(models.Model):

    """
    @note: 车型
    """
    name = models.CharField(max_length=128)
    serial = models.ForeignKey("Serial")
    year = models.CharField(max_length=16, db_index=True)
    ex_id = models.IntegerField()
    img = models.CharField(max_length=256, null=True)
    original_price = models.FloatField(default=0)
    state = models.BooleanField(default=True, db_index=True)

    class Meta:
        unique_together = [("name", "year", "serial"), ]


class UserUsedCar(models.Model):

    """
    @note: 用户提交的二手车信息
    """
    car = models.ForeignKey("CarBasicInfo")
    get_license_time = models.DateTimeField(db_index=True)
    trip_distance = models.FloatField()
    mobile = models.CharField(max_length=32, null=True)
    ip = models.IPAddressField(null=True)
    price = models.FloatField(default=0)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)


class ExUsedCar(models.Model):

    """
    @note: 站外获取的二手车信息
    """
    name = models.CharField(max_length=128)
    source = models.IntegerField(db_index=True)
    ex_id = models.CharField(max_length=128, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = [("source", "ex_id",), ]
