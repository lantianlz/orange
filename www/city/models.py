# -*- coding: utf-8 -*-

from django.db import models


class City(models.Model):
    location_type_choices = ((0, u'区域'), (1, u'省'), (2, u'市'), (3, u'区'))
    province_type_choices = ((0, u'省'), (1, u'自治区'), (2, u'直辖市'), (3, u'特别行政区'))

    area = models.CharField(max_length=32, null=True, db_index=True)
    province = models.CharField(max_length=32, null=True, db_index=True)
    city = models.CharField(max_length=32, null=True, db_index=True)
    district = models.CharField(max_length=32, null=True, db_index=True)
    pinyin = models.CharField(verbose_name=u'city对应的拼音', max_length=32, null=True, unique=True)
    pinyin_abbr = models.CharField(verbose_name=u'city对应的拼音缩写', max_length=32, null=True, unique=True)
    location_type = models.IntegerField(choices=location_type_choices, db_index=True, null=True)
    province_type = models.IntegerField(choices=province_type_choices, db_index=True, null=True)
    sort_num = models.IntegerField(default=0, db_index=True)
    is_show = models.BooleanField(default=False, db_index=True)
    baidu_rank = models.IntegerField(default=999, db_index=True)
    car_wash_count = models.IntegerField(default=0, db_index=True)
    vote_count = models.IntegerField(default=0, db_index=True)
    note = models.TextField(null=True)

    class Meta:
        ordering = ["-sort_num", "id"]

    def get_url(self):
        return ''

    def get_short_name(self):
        keys = [u"市", u"自治州", u"地区", u"区", u"县", u"其他"]
        name = u"未知类型"
        if self.location_type == 2:
            name = self.city
        elif self.location_type == 3:
            name = self.district
        for key in keys:
            name = name.replace(key, '')
        return name
