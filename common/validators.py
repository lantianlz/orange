# -*- coding: utf-8 -*-


"""
@attention: 校验方法封装
@author: lizheng
@date: 2013-12-09
"""


import re


class VerifyError(Exception):
    pass


def vlen(s, min_l, max_l):
    if min_l <= len(s) <= max_l:
        return
    raise VerifyError, u"长度超过范围(%s,%s)" % (min_l, max_l)


def vemail(s, min_len=3, max_len=50):
    re_str = ur"^[-_A-Za-z0-9\.]+@([-_A-Za-z0-9]+\.)+[A-Za-z0-9]{2,32}$"
    vlen(s, min_len, max_len)
    if not re.match(re_str, s):
        raise VerifyError, u"邮箱格式不正确"


def vnick(value, min_len=2, max_len=12, check_ban=True):
    """
    @attention: 验证昵称
    """
    if check_ban:
        ban_keywords = [u'测试', u'test', u'三点十分']
        for key in ban_keywords:
            if key in value:
                raise VerifyError, u"昵称不能含有关键字 %s ！" % key

    if not value.startswith("weixin_"):
        re_str = u'^[\w\-\_\u4e00-\u9fa5]{%s,%s}$' % (min_len, max_len)
        if not re.match(re_str, value):
            raise VerifyError, u"昵称只能是%s~%s位中文、字母、数字、下划线或减号！" % (min_len, max_len)


def vpassword(value):
    '''
    @note: 判断是否是弱密码
    '''
    weak_password = [
        '000000', '111111', '11111111', '112233', '123123', '123321', '123456', '12345678',
        '654321', '666666', '888888', 'abcdef', 'abcabc', 'abc123', 'a1b2c3',
        'aaa111', '123qwe', 'qwerty', 'qweasd', 'password',
        'p@ssword', 'passwd', 'iloveyou', '5201314'
    ]
    if value in weak_password:
        raise VerifyError, u"你的密码太过简单！请重新设置"
    use_char = set(list(value))
    if len(use_char) > 2:
        return
    raise VerifyError, u"你的密码太过简单！请重新设置"
