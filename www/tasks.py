# -*- coding: utf-8 -*-

import logging
import datetime
from celery.task import task


def async_send_email(emails, title, content, type='text'):
    '''
    @note: 由于调用较多，包装一层，用于控制是否异步调用
    '''
    from django.conf import settings
    if settings.LOCAL_FLAG:
        async_send_email_worker(emails, title, content, type)
    else:
        async_send_email_worker.delay(emails, title, content, type)


@task(queue='email_worker', name='email_worker.email_send')
def async_send_email_worker(emails, title, content, type='text'):
    from common import utils
    return utils.send_email(emails, title, content, type)


@task(queue='www_worker', name='www_worker.async_clear_count_info_by_code')
def async_clear_count_info_by_code(user_id, code):
    from www.message import interface
    return interface.UnreadCountBase().clear_count_info_by_code(user_id, code)


@task(queue='www_worker', name='www_worker.async_change_profile_from_weixin')
def async_change_profile_from_weixin(user, app_key, openid):
    from www.account.interface import UserBase
    UserBase().change_profile_from_weixin(user, app_key, openid)


@task(queue='www_worker', name='www_worker.async_send_buy_success_template_msg_by_user_id')
def async_send_buy_success_template_msg_by_user_id(user_id, name, remark, app_key=None):
    """
    @note: 发送洗车码购买成功模板消息
    """
    from www.weixin.interface import WexinBase
    from www.account.interface import ExternalTokenBase

    openid = ExternalTokenBase().get_weixin_openid_by_user_id(user_id)
    if openid:
        errcode, errmsg = WexinBase().send_buy_success_template_msg(openid=openid, name=name, remark=remark, app_key=app_key)
        # errcode, errmsg = WexinBase().send_buy_success_template_msg(openid="oNYsJj1eg4fnU4tKLvH-f2IXlxJ4", name=name, remark=remark, app_key="orange")
        logging.error(u"%s: errcode is:%s, errmsg is:%s" % (str(datetime.datetime.now()), errcode, errmsg))


@task(queue='www_worker', name='www_worker.async_send_use_order_code_template_msg_by_user_id')
def async_send_use_order_code_template_msg_by_user_id(user_id, product_type, name, time, remark, app_key=None):
    """
    note: 发送洗车码成功使用模板消息
    """
    from www.weixin.interface import WexinBase
    from www.account.interface import ExternalTokenBase

    openid = ExternalTokenBase().get_weixin_openid_by_user_id(user_id)
    if openid:
        errcode, errmsg = WexinBase().send_use_order_code_template_msg(openid=openid, product_type=product_type, name=name,
                                                                       time=time, remark=remark, app_key=app_key)
        # errcode, errmsg = WexinBase().send_use_order_code_template_msg(openid="oNYsJj1eg4fnU4tKLvH-f2IXlxJ4", product_type=product_type, name=name,
        #                                                                time=time, remark=remark,  app_key="orange")
        logging.error(u"%s: errcode is:%s, errmsg is:%s" % (str(datetime.datetime.now()), errcode, errmsg))
