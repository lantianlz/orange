# -*- coding: utf-8 -*-

import datetime
import logging
import time
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache, raw_sql
from www.misc.decorators import cache_required
from www.misc import consts
from www.tasks import async_send_email
from www.account.models import User, Profile, UserCount, LastActive, ActiveDay, ExternalToken

dict_err = {
    10100: u'邮箱重复',
    10101: u'昵称重复',
    10102: u'手机号重复',
    10103: u'被逮到了，无效的性别值',
    10104: u'这么奇葩的生日怎么可能',
    10105: u'两次输入密码不相同',
    10106: u'当前密码错误',
    10107: u'新密码和老密码不能相同',
    10108: u'登陆密码验证失败',
    10109: u'新邮箱和老邮箱不能相同',
    10110: u'邮箱验证码错误或者已过期，请重新验证',
    10111: u'该邮箱尚未注册',
    10112: u'code已失效，请重新执行重置密码操作',
    10113: u'没有找到对象',
}
dict_err.update(consts.G_DICT_ERROR)

ACCOUNT_DB = 'account'


class UserBase(object):

    def __init__(self):
        from common import password_hashers
        self.hasher = password_hashers.MD5PasswordHasher()

    def set_password(self, raw_password):
        assert raw_password
        self.password = self.hasher.make_password(raw_password)
        return self.password

    def check_password(self, raw_password, password):
        return self.hasher.check_password(raw_password, getattr(self, 'password', password))

    def set_profile_login_att(self, profile, user):
        for key in ['email', 'mobilenumber', 'username', 'last_login', 'password', 'state']:
            setattr(profile, key, getattr(user, key))
        # profile.is_staff = lambda:user.is_staff()
        setattr(profile, 'user_login', user)

    def get_user_login_by_id(self, id):
        try:
            user = User.objects.get(id=id, state__gt=0)
            return user
        except User.DoesNotExist:
            return None

    @cache_required(cache_key='user_%s', expire=3600, cache_config=cache.CACHE_USER)
    def get_user_by_id(self, id, state=[1, 2], must_update_cache=False):
        try:
            profile = Profile.objects.get(id=id)
            user = User.objects.get(id=profile.id, state__in=state)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return ''

    def get_user_by_nick(self, nick, state=[1, 2]):
        try:
            profile = Profile.objects.get(nick=nick)
            user = User.objects.get(id=profile.id, state__in=state)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def get_user_by_email(self, email):
        try:
            user = User.objects.get(email=email, state__gt=0)
            profile = Profile.objects.get(id=user.id)
            self.set_profile_login_att(profile, user)
            return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def get_user_by_mobilenumber(self, mobilenumber):
        try:
            if mobilenumber:
                user = User.objects.get(mobilenumber=mobilenumber, state__gt=0)
                profile = Profile.objects.get(id=user.id)
                self.set_profile_login_att(profile, user)
                return profile
        except (Profile.DoesNotExist, User.DoesNotExist):
            return None

    def check_user_info(self, email, nick, password, mobilenumber):
        try:
            validators.vemail(email)
            validators.vnick(nick)
            validators.vpassword(password)
        except Exception, e:
            return 99900, smart_unicode(e)

        if self.get_user_by_email(email):
            return 10100, dict_err.get(10100)
        if self.get_user_by_nick(nick):
            return 10101, dict_err.get(10101)
        if self.get_user_by_mobilenumber(mobilenumber):
            return 10102, dict_err.get(10102)
        return 0, dict_err.get(0)

    def check_gender(self, gender):
        if not str(gender) in ('0', '1', '2'):
            return 10103, dict_err.get(10103)
        return 0, dict_err.get(0)

    def check_birthday(self, birthday):
        try:
            birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d')
            now = datetime.datetime.now()
            assert (now + datetime.timedelta(days=100 * 365)) > birthday > (now - datetime.timedelta(days=100 * 365))
        except:
            return 10104, dict_err.get(10104)
        return 0, dict_err.get(0)

    @transaction.commit_manually(using=ACCOUNT_DB)
    def regist_user(self, email, nick, password, re_password, ip, mobilenumber=None, username=None,
                    source=0, gender=0, invitation_code=None):
        '''
        @note: 注册
        '''
        try:
            if not (email and nick and password):
                transaction.rollback(using=ACCOUNT_DB)
                return 99800, dict_err.get(99800)

            if password != re_password:
                transaction.rollback(using=ACCOUNT_DB)
                return 10105, dict_err.get(10105)

            errcode, errmsg = self.check_user_info(email, nick, password, mobilenumber)
            if errcode != 0:
                transaction.rollback(using=ACCOUNT_DB)
                return errcode, errmsg

            id = utils.uuid_without_dash()
            now = datetime.datetime.now()

            user = User.objects.create(id=id, email=email, mobilenumber=mobilenumber, last_login=now,
                                       password=self.set_password(password))
            profile = Profile.objects.create(id=id, nick=nick, ip=ip, source=source, gender=gender)
            self.set_profile_login_att(profile, user)

            transaction.commit(using=ACCOUNT_DB)

            # 发送验证邮件
            # self.send_confirm_email(user)

            return 0, profile
        except Exception, e:
            debug.get_debug_detail(e)
            transaction.rollback(using=ACCOUNT_DB)
            return 99900, dict_err.get(99900)

    def change_profile(self, user, nick, gender, birthday, des=None, state=None):
        '''
        @note: 资料修改
        '''
        user_id = user.id
        if not (user_id and nick and gender and birthday):
            return 99800, dict_err.get(99800)

        try:
            validators.vnick(nick)
        except Exception, e:
            return 99900, smart_unicode(e)

        if user.nick != nick and self.get_user_by_nick(nick):
            return 10101, dict_err.get(10101)

        errcode, errmsg = self.check_gender(gender)
        if errcode != 0:
            return errcode, errmsg

        errcode, errmsg = self.check_birthday(birthday)
        if errcode != 0:
            return errcode, errmsg

        user = self.get_user_by_id(user_id)
        user.nick = nick
        user.gender = int(gender)
        user.birthday = birthday
        if des:
            user.des = utils.filter_script(des)[:128]

        if state is not None:
            user_login = self.get_user_login_by_id(user.id)
            user_login.state = state
            user_login.save()

        user.save()

        # 更新缓存
        self.get_user_by_id(user.id, must_update_cache=True)
        return 0, user

    def change_pwd(self, user, old_password, new_password_1, new_password_2):
        '''
        @note: 密码修改
        '''
        if not all((old_password, new_password_1, new_password_2)):
            return 99800, dict_err.get(99800)

        if new_password_1 != new_password_2:
            return 10105, dict_err.get(10105)
        if not self.check_password(old_password, user.password):
            return 10106, dict_err.get(10106)
        if old_password == new_password_1:
            return 10107, dict_err.get(10107)
        try:
            validators.vpassword(new_password_1)
        except Exception, e:
            return 99900, smart_unicode(e)

        user_login = self.get_user_login_by_id(user.id)
        user_login.password = self.set_password(new_password_1)
        user_login.save()

        # 更新缓存
        self.get_user_by_id(user.id, must_update_cache=True)
        return 0, dict_err.get(0)

    def change_email(self, user, email, password):
        '''
        @note: 邮箱修改
        '''
        if not all((email, password)):
            return 99800, dict_err.get(99800)

        if not self.check_password(password, user.password):
            return 10108, dict_err.get(10108)

        if user.email == email:
            return 10109, dict_err.get(10109)

        try:
            validators.vemail(email)
        except Exception, e:
            return 99900, smart_unicode(e)

        if user.email != email and self.get_user_by_email(email):
            return 10100, dict_err.get(10100)

        user_login = self.get_user_login_by_id(user.id)
        user_login.email = email
        user_login.save()

        # 更新缓存
        self.get_user_by_id(user.id, must_update_cache=True)

        # 发送验证邮件
        self.send_confirm_email(user)

        return 0, dict_err.get(0)

    def send_confirm_email(self, user):
        '''
        @note: 发送验证邮件
        '''
        cache_obj = cache.Cache()
        key = u'confirm_email_code_%s' % user.id
        code = cache_obj.get(key)
        if not code:
            code = utils.uuid_without_dash()
            cache_obj.set(key, code, time_out=1800)

        if not cache_obj.get_time_is_locked(key, 60):
            context = {'verify_url': '%s/account/user_settings/verify_email?code=%s' % (settings.MAIN_DOMAIN, code), }
            async_send_email(user.email, u'三点十分邮箱验证', utils.render_email_template('email/verify_email.html', context), 'html')

    def check_email_confim_code(self, user, code):
        '''
        @note: 确认邮箱
        '''
        if not code:
            return 99800, dict_err.get(99800)

        cache_obj = cache.Cache()
        key = u'confirm_email_code_%s' % user.id
        cache_code = cache_obj.get(key)

        if cache_code != code:
            return 10110, dict_err.get(10110)

        user.email_verified = True
        user.save()

        # 更新缓存
        self.get_user_by_id(user.id, must_update_cache=True)
        return 0, user

    def send_forget_password_email(self, email):
        '''
        @note: 发送密码找回邮件
        '''
        if not email:
            return 99800, dict_err.get(99800)

        user = self.get_user_by_email(email)
        if not user:
            return 10111, dict_err.get(10111)
        cache_obj = cache.Cache()
        key = u'forget_password_email_code_%s' % email
        code = cache_obj.get(key)
        if not code:
            code = utils.uuid_without_dash()
            cache_obj.set(key, code, time_out=1800)
            cache_obj.set(code, user, time_out=1800)

        if not cache_obj.get_time_is_locked(key, 60):
            context = {'reset_url': '%s/reset_password?code=%s' % (settings.MAIN_DOMAIN, code), }
            async_send_email(email, u'三点十分找回密码', utils.render_email_template('email/reset_password.html', context), 'html')
        return 0, dict_err.get(0)

    def get_user_by_code(self, code):
        cache_obj = cache.Cache()
        return cache_obj.get(code)

    def reset_password_by_code(self, code, new_password_1, new_password_2):
        user = self.get_user_by_code(code)
        if not user:
            return 10112, dict_err.get(10112)

        if new_password_1 != new_password_2:
            return 10105, dict_err.get(10105)
        try:
            validators.vpassword(new_password_1)
        except Exception, e:
            return 99900, smart_unicode(e)

        user_login = self.get_user_login_by_id(user.id)
        user_login.password = self.set_password(new_password_1)
        user_login.save()

        # 更新缓存
        self.get_user_by_id(user.id, must_update_cache=True)

        cache_obj = cache.Cache()
        key = u'forget_password_email_code_%s' % user.email
        cache_obj.delete(key)
        cache_obj.delete(code)
        return 0, user_login

    def update_user_last_active_time(self, user_id, ip=None, last_active_source=0):
        '''
        @note: 更新用户最后活跃时间
        '''
        cache_obj = cache.Cache()
        # 一小时更新一次
        if not cache_obj.get_time_is_locked(key=u'last_active_time_%s' % user_id, time_out=3600):
            try:
                la = LastActive.objects.get(user_id=user_id)
                la.ip = ip
                la.last_active_source = last_active_source
                la.last_active_time = datetime.datetime.now()
                la.save()
            except LastActive.DoesNotExist:
                LastActive.objects.create(user_id=user_id, last_active_time=datetime.datetime.now(),
                                          ip=ip, last_active_source=last_active_source)
            now_date = datetime.datetime.now().date()
            try:
                ActiveDay.objects.get(user_id=user_id, active_day=now_date)
            except ActiveDay.DoesNotExist:
                ActiveDay.objects.create(user_id=user_id, active_day=now_date)

    def update_user_last_login_time(self, user_id, ip=None, last_active_source=0):
        user_login = self.get_user_login_by_id(user_id)
        user_login.last_login = datetime.datetime.now()
        user_login.save()
        self.update_user_last_active_time(user_id, ip, last_active_source)

    def get_all_users(self):
        '''
        '''
        return User.objects.all()

    def format_user_full_info(self, user_id):
        '''
        格式化完整用户信息
        '''
        format_user = self.get_user_by_id(user_id)

        # 统计信息
        format_user.user_count = UserCountBase().get_user_count_info(user_id)

        # 是否管理员
        from www.admin.interface import PermissionBase
        if PermissionBase().get_user_permissions(user_id):
            format_user.is_admin = True
        else:
            format_user.is_admin = False

        # 活跃时间
        la = LastActive.objects.filter(user_id=user_id)
        if la:
            la = la[0]
            format_user.last_active = la.last_active_time
            format_user.last_active_ip = la.ip
            format_user.last_active_source = la.last_active_source
        else:
            format_user.last_active = format_user.create_time
            format_user.last_active_ip = format_user.ip
            format_user.last_active_source = ''

        # 注册来源
        format_user.source_display = u"直接注册"
        if format_user.source > 0:
            ets = list(ExternalToken.objects.filter(user_id=user_id))
            if ets:
                format_user.source_display = ets[0].get_source_display()

        return format_user

    def format_user_with_count_info(self, user):
        """
        @note: 给用户设置上统计数字信息
        """
        user_count_info = UserCountBase().get_user_count_info(user.id)
        user.user_journey_count = user_count_info['user_journey_count']
        user.user_answer_count = user_count_info['user_answer_count']
        user.user_liked_count = user_count_info['user_liked_count']
        user.following_count = user_count_info['following_count']
        user.follower_count = user_count_info['follower_count']
        return user

    def get_active_users(self, date):

        return LastActive.objects.filter(last_active_time__gte=date)

    def get_users_by_range_date(self, start_date, end_date):
        return User.objects.filter(create_time__range=(start_date, end_date))

    def search_users(self, nick):
        if not nick:
            return []
        return Profile.objects.filter(nick__icontains=nick)[:200]

    def get_user_by_external_info(self, source, access_token, external_user_id,
                                  refresh_token, nick, ip, expire_time,
                                  user_url='', gender=0, app_id=None):
        assert all((source, access_token, external_user_id, nick))

        expire_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time()) + int(expire_time)))
        et = self.get_external_user(source, access_token, external_user_id, refresh_token, expire_time)
        if et:
            return True, self.get_user_by_id(et.user_id)
        else:
            email = '%s_%s@mr3-10.club' % (source, int(time.time() * 1000))
            nick = self.generate_nick_by_external_nick(nick)
            if not nick:
                return False, u'生成名称异常'
            errcode, result = self.regist_user(email=email, nick=nick, password=email, re_password=email, ip=ip, source=1, gender=gender)
            if errcode == 0:
                user = result
                ExternalToken.objects.create(source=source, external_user_id=external_user_id,
                                             access_token=access_token, refresh_token=refresh_token, user_url=user_url,
                                             nick=nick, user_id=user.id, expire_time=expire_time, app_id=app_id
                                             )
                return True, user
            else:
                return False, result

    def generate_nick_by_external_nick(self, nick):
        if not self.get_user_by_nick(nick):
            return nick
        else:
            for i in xrange(3):
                new_nick = '%s_%s' % (nick, i)
                if not self.get_user_by_nick(new_nick):
                    return new_nick
            for i in xrange(10):
                return '%s_%s' % (nick,  str(int(time.time() * 1000))[-3:])

    def get_external_user(self, source, access_token, external_user_id, refresh_token, expire_time):
        assert all((source, access_token, external_user_id))

        et = None
        ets = list(ExternalToken.objects.filter(source=source, external_user_id=external_user_id))
        if ets:
            et = ets[0]
            if et.access_token != access_token:
                et.access_token = access_token
                et.refresh_token = refresh_token
                et.expire_time = expire_time
                et.save()
        else:
            ets = list(ExternalToken.objects.filter(source=source, access_token=access_token))
            if ets:
                et = ets[0]
                if et.external_user_id != external_user_id:
                    et.external_user_id = external_user_id
                    et.refresh_token = refresh_token
                    et.expire_time = expire_time
                    et.save()
        return et

    def change_user_city(self, user_id, city_id):
        '''
        @note: 修改城市信息
        '''
        user = self.get_user_by_id(user_id)
        user.city_id = city_id
        user.save()

        # 更新缓存
        self.get_user_by_id(user.id, must_update_cache=True)
        return 0, user

    def get_user_for_admin(self, user_nick="", email=""):
        objs = None

        if user_nick:
            objs = self.get_user_by_nick(user_nick)
            objs = [objs] if objs else []
        elif email:
            objs = self.get_user_by_email(email)
            objs = [objs] if objs else []
        else:
            objs = User.objects.all()

        return objs

    def change_profile_from_weixin(self, user, app_key, openid):
        '''
        @note: 通过微信资料修改
        '''
        try:
            import urllib2
            from www.misc import qiniu_client
            from www.weixin.interface import dict_weixin_app, WexinBase

            if user.nick.startswith("weixin_"):
                user_id = user.id
                app_id = dict_weixin_app[app_key]["app_id"]

                weixin_user_info = WexinBase().get_user_info(app_key, openid)
                if weixin_user_info:
                    nick = weixin_user_info["nickname"]
                    gender = weixin_user_info["sex"]
                    errcode, errmsg = self.check_gender(gender)
                    if errcode != 0:
                        return errcode, errmsg

                    weixin_img_url = weixin_user_info.get("headimgurl")
                    user_avatar = ''
                    if weixin_img_url:
                        # 上传图片

                        flag, img_name = qiniu_client.upload_img(urllib2.urlopen(weixin_img_url, timeout=20), img_type='weixin_avatar')
                        if flag:
                            user_avatar = '%s/%s' % (settings.IMG0_DOMAIN, img_name)
                        else:
                            logging.error(u'转换微信图片失败，weixin_img_url is %s' % weixin_img_url)

                    ets = list(ExternalToken.objects.filter(app_id=app_id, external_user_id=openid, source="weixin"))
                    if ets:
                        et = ets[0]
                        et.nick = nick
                        et.save()

                    nick = self.generate_nick_by_external_nick(nick)
                    user = self.get_user_by_id(user_id)
                    user.nick = nick
                    user.avatar = user_avatar
                    user.gender = int(gender)
                    user.save()

                    # 更新缓存
                    self.get_user_by_id(user.id, must_update_cache=True)
            return 0, user
        except Exception, e:
            debug.get_debug_detail(e)

    def login_by_weixin_qr_code(self, ticket, openid, app_key):
        """
        @note: 通过微信二维码扫码登陆
        """
        assert ticket and openid and app_key
        from www.weixin.interface import dict_weixin_app
        from www.tasks import async_change_profile_from_weixin

        user_info = dict(nick=u"weixin_%s" % int(time.time() * 1000), url="", gender=0)
        flag, result = self.get_user_by_external_info(source='weixin', access_token="access_token_%s" % openid, external_user_id=openid,
                                                      refresh_token=None, nick=user_info['nick'], ip=None, expire_time=0,
                                                      user_url=user_info['url'], gender=user_info['gender'], app_id=dict_weixin_app[app_key]["app_id"])
        if flag:
            user = result
            UserBase().update_user_last_login_time(user.id, last_active_source=2)

            # 更新用户资料
            if settings.LOCAL_FLAG:
                async_change_profile_from_weixin(user, app_key, openid)
            else:
                async_change_profile_from_weixin.delay(user, app_key, openid)

            errcode, errmsg = 0, u"扫码登陆网站成功"
        else:
            errcode, errmsg = -1, result

        # 设置缓存
        cache_obj = cache.Cache()
        key = u'weixin_login_state_%s' % ticket
        user_id = user.id if errcode == 0 else ""
        cache_obj.set(key, [errcode, errmsg, user_id], time_out=300)

        return errcode, errmsg

    def change_pwd_by_admin(self, user_id, pwd):

        try:

            try:
                validators.vpassword(pwd)
            except Exception, e:
                return 99900, smart_unicode(e)

            user = self.get_user_login_by_id(user_id)
            user.password = self.set_password(pwd)
            user.save()

            # 更新缓存
            self.get_user_by_id(user.id, must_update_cache=True)
        except Exception:
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def get_count_group_by_create_time(self, count=360):
        '''
        查询用户数量 按创建时间分组
        数据格式：
        [2014-01-01, 15], [2014-01-02, 23]
        '''
        sql = """
            SELECT DATE_FORMAT(create_time, "%%Y-%%m-%%d"), COUNT(*) 
            FROM account_orange.account_user 
            GROUP BY DATE_FORMAT(create_time, "%%Y-%%m-%%d")
            LIMIT 0, %s
        """

        return raw_sql.exec_sql(sql, [count], 'account')

    def get_toady_count_group_by_create_time(self):
        '''
        查询当天用户数量 按创建时间分组
        数据格式：
        [09, 15], [10, 23]
        '''
        sql = """
            SELECT DATE_FORMAT(create_time, "%%H"), COUNT(*) 
            FROM account_orange.account_user 
            WHERE %s <= create_time AND create_time <= %s
            GROUP BY DATE_FORMAT(create_time, "%%H")
        """
        now = datetime.datetime.now().strftime('%Y-%m-%d')

        return raw_sql.exec_sql(sql, [now + ' 00:00:00', now + ' 23:59:59'], 'account')


def user_profile_required(func):
    '''
    @note: 访问用户控件装饰器
    '''
    def _decorator(request, user_id, *args, **kwargs):
        from www.timeline.interface import UserFollowBase
        from django.shortcuts import render_to_response
        from django.template import RequestContext

        ufb = UserFollowBase()
        ub = UserBase()
        if not user_id:
            user = request.user
        else:
            user = ub.get_user_by_id(user_id)
            if not user:
                err_msg = u'用户不存在'
                return render_to_response('error.html', locals(), context_instance=RequestContext(request))
        request.is_me = (request.user == user)
        if not request.is_me:
            request.is_follow = ufb.check_is_follow(request.user.id, user.id)

        user_count_info = UserCountBase().get_user_count_info(user_id)
        request.user_journey_count = user_count_info['user_journey_count']
        request.user_answer_count = user_count_info['user_answer_count']
        request.user_liked_count = user_count_info['user_liked_count']
        request.following_count = user_count_info['following_count']
        request.follower_count = user_count_info['follower_count']

        return func(request, user, *args, **kwargs)
    return _decorator


class UserCountBase(object):

    def __init__(self):
        pass

    @cache_required(cache_key='user_count_info_%s', expire=3600 * 24)
    def get_user_count_info(self, user_id, must_update_cache=False):
        try:
            uc = UserCount.objects.get(user_id=user_id)
            return dict(user_journey_count=uc.user_journey_count, user_answer_count=uc.user_answer_count,
                        user_liked_count=uc.user_liked_count, following_count=uc.following_count,
                        follower_count=uc.follower_count)
        except UserCount.DoesNotExist:
            return dict(user_journey_count=0, user_answer_count=0, user_liked_count=0,
                        following_count=0, follower_count=0)

    def update_user_count(self, user_id, code, operate="add"):
        assert (user_id and code)
        uc, created = UserCount.objects.get_or_create(user_id=user_id)
        count = getattr(uc, code)
        if operate == 'add':
            count += 1
        else:
            count -= 1
        setattr(uc, code, count)
        uc.save()

        # 更新缓存
        self.get_user_count_info(user_id, must_update_cache=True)

    @cache_required(cache_key='user_order_by_answer_count', expire=3600)
    def get_user_order_by_answer_count(self, must_update_cache=False, count=21):
        ucs = UserCount.objects.all()
        return list(ucs.order_by('-user_answer_count')[:count])

    def get_show_invite_users(self, exclude_user_id, count=20):
        '''
        @note: 获取邀请用户展示
        '''
        ucs = self.get_user_order_by_answer_count()
        data = [uc for uc in ucs if uc.user_id != exclude_user_id]
        return data[:count]

    def get_all_users_by_order_count(self, sort):
        '''
        '''
        return UserCount.objects.all().order_by("-" + sort)


class ExternalTokenBase(object):

    def get_ets_by_user_id(self, user_id, source=None):
        ps = dict(user_id=user_id)
        if source is not None:
            ps.update(dict(source=source))
        return ExternalToken.objects.filter(**ps)

    def get_weixin_openid_by_user_id(self, user_id):
        ets = list(self.get_ets_by_user_id(user_id, source="weixin"))
        if ets:
            return ets[0].external_user_id

    def get_external_for_admin(self, s_date, e_date, nick=''):

        # objs = ExternalToken.objects.filter(create_time__range=(s_date, e_date))
        objs = ExternalToken.objects.all()

        if nick:
            objs = objs.filter(nick=nick)
        return objs
