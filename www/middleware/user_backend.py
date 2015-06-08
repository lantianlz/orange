# -*- coding: utf-8 -*-

import datetime
from www.account.interface import UserBase


def _save(*argv, **kwargs):
    pass


class AuthBackend(object):
    supports_inactive_user = True

    def authenticate(self, username=None, password=None):
        ub = UserBase()
        user = ub.get_user_by_email(username)
        if not user:
            user = ub.get_user_by_mobilenumber(username)
        if user and ub.check_password(password, user.password):
            # 更新最后登录时间
            user_login = user.user_login
            user_login.last_login = datetime.datetime.now()
            user_login.save()

            user.save = _save
            # 更新缓存
            ub.get_user_by_id(user.id, must_update_cache=True)
            return user

    def get_user(self, user_id):
        user = UserBase().get_user_by_id(user_id)
        return user
