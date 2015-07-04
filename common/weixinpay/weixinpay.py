# -*- coding: utf-8 -*-


import os
import sys

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
# 引入父目录来引入其他模块
sys.path.extend([os.path.abspath(os.path.join(SITE_ROOT, '../')),
                 os.path.abspath(os.path.join(SITE_ROOT, '../../')),
                 ])
os.environ['DJANGO_SETTINGS_MODULE'] = 'www.settings'


import requests
import logging

from pprint import pprint
from pyquery import PyQuery as pq
from django.utils.encoding import smart_str
from common.hashcompat import md5_constructor as md5

from common.weixinpay.config_real import settings
from common import debug, utils


MAIN_DOMAIN = 'http://www.3-10.cc'
WEIXINPAY_URL = 'https://api.mch.weixin.qq.com'


class Weixinpay(object):

    def __init__(self):
        self.appid = settings.APPID
        self.mch_id = settings.MCH_ID
        self.sign_key = settings.SIGN_KEY
        self.input_charset = "utf8"

    def format_params(self, params):
        ks = params.keys()
        ks.sort()
        newparams = {}
        prestr = ''
        for k in ks:
            v = params[k]
            k = smart_str(k, self.input_charset)
            newparams[k] = smart_str(v, self.input_charset)
            if k not in ('sign', 'sign_type') and v != '':
                prestr += '%s=%s&' % (k, newparams[k])
        prestr = prestr[:-1]
        return newparams, prestr

    def build_mysign(self, prestr):
        """
        @note: md5签名, 转成大写
        """
        return md5("%s&key=%s" % (prestr, self.sign_key)).hexdigest().upper()

    def get_prepay_id(self, body, out_trade_no, total_fee, openid, attach="", trade_type="JSAPI", ip="121.42.48.184", notify_url=None):
        """
        @note: total_fee单位为分，不能带小数点
        """
        url = "%s/pay/unifiedorder" % WEIXINPAY_URL
        notify_url = notify_url or ("%s/weixinnotify" % MAIN_DOMAIN)

        params = dict(appid=self.appid, mch_id=self.mch_id,
                      nonce_str=utils.uuid_without_dash(), body=body, attach=attach,
                      out_trade_no=out_trade_no, total_fee=total_fee, spbill_create_ip=ip,
                      notify_url=notify_url, trade_type=trade_type, openid=openid)

        params, prestr = self.format_params(params)
        sign = self.build_mysign(prestr)
        params["sign"] = sign

        xml = """
        <xml>
        <appid>%(appid)s</appid>
        <attach><![CDATA[%(attach)s]]></attach>
        <body><![CDATA[%(body)s]]></body>
        <mch_id>%(mch_id)s</mch_id>
        <nonce_str>%(nonce_str)s</nonce_str>
        <notify_url>%(notify_url)s</notify_url>
        <out_trade_no>%(out_trade_no)s</out_trade_no>
        <spbill_create_ip>%(spbill_create_ip)s</spbill_create_ip>
        <total_fee>%(total_fee)s</total_fee>
        <trade_type>%(trade_type)s</trade_type>
        <openid><![CDATA[%(openid)s]]></openid>
        <sign><![CDATA[%(sign)s]]></sign>
        </xml>
        """ % params

        try:
            resp = requests.post(url=url, data=xml, timeout=30)
            resp.encoding = "utf-8"
            text = resp.text
            # text = """
            # <xml><return_code><![CDATA[SUCCESS]]></return_code>
            # <return_msg><![CDATA[OK]]></return_msg>
            # <appid><![CDATA[wx23cca542b396c669]]></appid>
            # <mch_id><![CDATA[1224504302]]></mch_id>
            # <nonce_str><![CDATA[YGJzdXq7hggzwGVx]]></nonce_str>
            # <sign><![CDATA[08AC09CF26D2820E833F857E61DE4B62]]></sign>
            # <result_code><![CDATA[SUCCESS]]></result_code>
            # <prepay_id><![CDATA[wx2014121518153157cbc1f6af0195338906]]></prepay_id>
            # <trade_type><![CDATA[JSAPI]]></trade_type>
            # </xml>
            # """
            text = smart_str(text)
            if "prepay_id" in text:
                jq = pq(text)
                prepay_id = jq('prepay_id').html()
                self.prepay_id = prepay_id

                return True, prepay_id
            else:
                from www.tasks import async_send_email
                from django.conf import settings
                from django.utils.encoding import smart_unicode

                logging.error(u"get_prepay_id fail, info is:%s" % text)
                logging.error(u"get_prepay_id fail, params is:%s" % smart_unicode(xml))

                title = u'%s 生成微信支付链接错误' % settings.SERVER_NAME
                content = u'params:%s\n\nreturn info:%s' % (smart_unicode(xml), text)
                async_send_email(settings.NOTIFICATION_EMAIL, title, content)

                return False, text
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return False, e

    def validate_notify_params(self, params):
        '''
        @note: 校验支付通知接口的参数是否正常
        '''
        sign_in = params.get("sign", "")

        params, prestr = self.format_params(params)
        sign = self.build_mysign(prestr)

        return sign == sign_in

    def format_xml_data_to_params(self, xml_data):
        params = {}
        jq = pq(xml_data)
        for children in jq.children():
            params[children.tag.strip()] = children.text.strip()
        # pprint(params)
        return params


if __name__ == '__main__':
    weixinpay = Weixinpay()
    # print weixinpay.get_prepay_id(body=u"三点十分", out_trade_no="W2014120815441258305", total_fee=2000, openid="oNYsJj1eg4fnU4tKLvH-f2IXlxJ4")

    xml_data = """
    <xml><appid><![CDATA[wx23cca542b396c669]]></appid>
    <bank_type><![CDATA[CMB_DEBIT]]></bank_type>
    <cash_fee><![CDATA[1]]></cash_fee>
    <fee_type><![CDATA[CNY]]></fee_type>
    <is_subscribe><![CDATA[Y]]></is_subscribe>
    <mch_id><![CDATA[1224504302]]></mch_id>
    <nonce_str><![CDATA[1ed469c2845311e48cab00163e0237be]]></nonce_str>
    <openid><![CDATA[oNYsJj1eg4fnU4tKLvH-f2IXlxJ4]]></openid>
    <out_trade_no><![CDATA[W2014121520084622604]]></out_trade_no>
    <result_code><![CDATA[SUCCESS]]></result_code>
    <return_code><![CDATA[SUCCESS]]></return_code>
    <sign><![CDATA[79BA77410E75E7F0F7ADA8C91D16EFEA]]></sign>
    <time_end><![CDATA[20141215200914]]></time_end>
    <total_fee>1</total_fee>
    <trade_type><![CDATA[JSAPI]]></trade_type>
    <transaction_id><![CDATA[1008790051201412150007265351]]></transaction_id>
    </xml>
    """

    params = weixinpay.format_xml_data_to_params(xml_data)
    pprint(params)
    print weixinpay.validate_notify_params(params)
