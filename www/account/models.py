# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.conf import settings


class User(models.Model):

    '''
    用户类
    '''
    state_choices = ((0, u'无效用户'), (1, u'有效用户'), (2, u'内部成员'), )

    auto_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=32, unique=True)
    email = models.CharField(verbose_name=u'邮箱', max_length=64, unique=True)
    mobilenumber = models.CharField(verbose_name=u'邮箱', max_length=32, null=True, unique=True)
    username = models.CharField(verbose_name=u'用户名', max_length=32, null=True, unique=True)
    password = models.CharField(verbose_name=u'密码', max_length=128)
    state = models.IntegerField(verbose_name=u'用户状态', default=1, choices=state_choices, db_index=True)
    last_login = models.DateTimeField(verbose_name=u'上次登陆时间', db_index=True)
    create_time = models.DateTimeField(verbose_name=u'创建时间', db_index=True, default=datetime.datetime.now)

    def is_staff(self):
        return self.state in (2, )

    def __unicode__(self):
        return '%s, %s' % (self.id, self.email)

    class Meta:
        ordering = ["-create_time"]


class Profile(models.Model):

    '''
    用户扩展信息
    '''
    gender_choices = ((0, u'未设置'), (1, u'男'), (2, u'女'), )
    source_choices = ((0, u'web'), (1, u'第三方登录'))

    auto_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=32, unique=True)
    nick = models.CharField(max_length=32, unique=True)
    domain = models.CharField(max_length=32, unique=True, null=True)
    birthday = models.DateField(default='2000-01-01', db_index=True)
    gender = models.IntegerField(verbose_name=u'性别', default=0, choices=gender_choices, db_index=True)
    city_id = models.IntegerField(default=0, db_index=True)
    avatar = models.CharField(verbose_name=u'头像', max_length=256, default='')
    email_verified = models.BooleanField(verbose_name=u'邮箱是否验证过', default=False)
    mobile_verified = models.BooleanField(verbose_name=u'手机是否验证过', default=False)
    ip = models.CharField(verbose_name=u'登陆ip', max_length=32, null=True)
    des = models.CharField(max_length=256, null=True)
    source = models.IntegerField(default=0, choices=source_choices)
    create_time = models.DateTimeField(verbose_name=u'创建时间', db_index=True, default=datetime.datetime.now)

    def is_staff(self):
        # 从user移植过来避免cPickle的dumps报错
        return self.state in (2, )

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_url(self):
        return u'/p/%s' % self.id

    def get_full_url(self):
        return u'%s%s' % (settings.MAIN_DOMAIN, self.get_url())

    def get_avatar(self, key=''):
        if self.avatar:
            return '%s%s' % (self.avatar, ('!%s' % key) if key else '')
        else:
            return '%simg/default_avatar.png' % settings.MEDIA_URL

    def get_avatar_600(self):
        return self.get_avatar(key='600m0')

    def get_avatar_450(self):
        return self.get_avatar(key='450m0')

    def get_avatar_300(self):
        return self.get_avatar(key='300m300')

    def get_avatar_100(self):
        return self.get_avatar(key='100m100')

    def get_avatar_65(self):
        return self.get_avatar(key='65m65')

    def get_avatar_25(self):
        return self.get_avatar(key='25m25')

    def get_ta_display(self):
        return {1: u'他', 2: u'她'}.get(self.gender, u'Ta')

    def get_permissions(self):
        '''
        获取用户权限
        '''
        return []

    def get_city_id(self):
        return self.city_id or 1974

    def __unicode__(self):
        return u'%s, %s' % (self.id, self.nick)


class UserChangeLog(models.Model):
    change_type_choices = ((0, u'密码'), (1, u'邮箱'), (2, u'手机'), )

    change_type = models.IntegerField(verbose_name=u'变更类型', choices=change_type_choices)
    befor = models.CharField(verbose_name=u'变更前', max_length=64, db_index=True)
    after = models.CharField(max_length=64, db_index=True, verbose_name=u'变更后')
    ip = models.CharField(verbose_name=u'操作ip', max_length=32, null=True)
    create_time = models.DateTimeField(verbose_name=u'创建时间', db_index=True, default=datetime.datetime.now)


class LastActive(models.Model):
    last_active_source_choices = ((0, u'web页面'), (1, u'手机app'), (2, u"微信"))

    user_id = models.CharField(max_length=32, unique=True)
    ip = models.CharField(max_length=32, null=True)
    last_active_time = models.DateTimeField(db_index=True)
    last_active_source = models.IntegerField(default=0, choices=last_active_source_choices)

    class Meta:
        ordering = ["-last_active_time"]


class ActiveDay(models.Model):
    user_id = models.CharField(max_length=32, db_index=True)
    active_day = models.DateField(db_index=True)

    class Meta:
        unique_together = [("user_id", "active_day"), ]


class BlackList(models.Model):
    type_choices = ((0, u'全部'), (1, u'禁止登陆'), (2, u'禁止发帖'))
    user_id = models.CharField(max_length=32, db_index=True)
    type = models.IntegerField(default=0, choices=type_choices)
    state = models.BooleanField(default=True)
    expire_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)


class UserCount(models.Model):
    user_id = models.CharField(max_length=32, unique=True)
    user_journey_count = models.IntegerField(default=0, db_index=True)
    user_answer_count = models.IntegerField(default=0, db_index=True)
    user_liked_count = models.IntegerField(default=0, db_index=True)
    following_count = models.IntegerField(default=0, db_index=True)
    follower_count = models.IntegerField(default=0, db_index=True)


class ExternalToken(models.Model):
    source_choices = ((u"qq", u"QQ"), (u"sina", u"新浪微博"), (u"weixin", u"微信"))

    user_id = models.CharField(max_length=32, db_index=True)
    source = models.CharField(max_length=16, db_index=True, choices=source_choices)
    access_token = models.CharField(max_length=255, db_index=True)
    refresh_token = models.CharField(max_length=255, null=True)
    external_user_id = models.CharField(max_length=128, db_index=True)
    union_id = models.CharField(max_length=128, null=True)  # 供微信多个公众号使用
    app_id = models.CharField(max_length=128, null=True)  # 对应的app_id
    nick = models.CharField(max_length=64, null=True)
    user_url = models.CharField(max_length=128, null=True)
    expire_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    state = models.BooleanField(default=True)

    class Meta:
        unique_together = [("source", "access_token"), ("source", "external_user_id")]
        ordering = ["-create_time"]
