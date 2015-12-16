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
import urlparse

# from pprint import pprint
from pyquery import PyQuery as pq
from django.utils.encoding import smart_str

from common.hashcompat import md5_constructor as md5
from common.alipay.config_real import settings
from common import debug


MAIN_DOMAIN = 'http://www.aoaoxc.com'
ALIPAY_URL = 'http://wappaygw.alipay.com/service/rest.htm'


class Alipay(object):

    def __init__(self):
        self.partner = settings.ALIPAY_PARTNER
        self.seller_account_name = settings.ALIPAY_SELLER_EMAIL
        self.input_charset = settings.ALIPAY_INPUT_CHARSET
        self.key = settings.ALIPAY_KEY
        self.format = "xml"
        self.v = "2.0"
        self.sec_id = 'MD5'
        self.pay_expire = 1440  # 有效期为1天，单位是分钟
        self.merchant_url = MAIN_DOMAIN

    def format_params(self, params):
        ks = params.keys()
        ks.sort()
        newparams = {}
        prestr = ''
        for k in ks:
            v = params[k]
            k = smart_str(k, self.input_charset)
            if k not in ('sign', 'sign_type') and v != '':
                newparams[k] = smart_str(v, self.input_charset)
                prestr += '%s=%s&' % (k, newparams[k])
        prestr = prestr[:-1]
        return newparams, prestr

    def build_mysign(self, prestr):
        """
        @note: md5签名
        """
        return md5(prestr + self.key).hexdigest()

    def create_token_params(self, subject, out_trade_no, total_fee, out_user, call_back_url=None, notify_url=None):
        req_data = (u"<direct_trade_create_req>"
                    "<subject>%(subject)s</subject>"
                    "<out_trade_no>%(out_trade_no)s</out_trade_no>"
                    "<total_fee>%(total_fee)s</total_fee>"
                    "<seller_account_name>%(seller_account_name)s</seller_account_name>"
                    "<call_back_url>%(call_back_url)s</call_back_url>"
                    "<notify_url>%(notify_url)s</notify_url>"
                    "<out_user>%(out_user)s</out_user>"
                    "<merchant_url>%(merchant_url)s</merchant_url>"
                    "<pay_expire>%(pay_expire)s</pay_expire>"
                    "</direct_trade_create_req>") % dict(subject=subject, out_trade_no=out_trade_no, total_fee=total_fee,
                                                         seller_account_name=self.seller_account_name, out_user=out_user, pay_expire=self.pay_expire,
                                                         merchant_url=self.merchant_url, call_back_url=call_back_url, notify_url=notify_url)
        params = {}
        params['req_data'] = req_data
        params['service'] = "alipay.wap.trade.create.direct"
        params['sec_id'] = self.sec_id
        params['partner'] = self.partner
        params['req_id'] = out_trade_no
        params['format'] = self.format
        params['v'] = self.v
        params, prestr = self.format_params(params)
        sign = self.build_mysign(prestr)
        params['sign'] = sign
        return params

    def get_token(self, subject, out_trade_no, total_fee, out_user, call_back_url=None, notify_url=None):
        call_back_url = call_back_url or ("%s/alipaycallback_m" % MAIN_DOMAIN)
        notify_url = notify_url or ("%s/alipaynotify_m" % MAIN_DOMAIN)

        params = self.create_token_params(subject, out_trade_no, total_fee, out_user, call_back_url, notify_url)

        try:
            resp = requests.post(ALIPAY_URL, data=params, timeout=30)
            text = resp.text
            text = urlparse.parse_qs(text)
            if text.has_key('res_data'):
                res_data = smart_str(text['res_data'][0])
                jq = pq(res_data)
                token = jq('request_token').html()
                self.token = token
                return True, token
            else:
                res_error = text['res_error']
                return False, res_error
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
            return False, e

    def get_pay_url(self):
        params = {}
        params['req_data'] = '<auth_and_execute_req><request_token>%s</request_token></auth_and_execute_req>' % self.token
        params['service'] = 'alipay.wap.auth.authAndExecute'
        params['sec_id'] = self.sec_id
        params['partner'] = self.partner
        params['v'] = self.v
        params['format'] = self.format
        params, prestr = self.format_params(params)
        sign = self.build_mysign(prestr)
        params['sign'] = sign

        self.pay_url = '%s?%s&sign=%s' % (ALIPAY_URL, prestr, sign)
        return self.pay_url

    def validate_html_redirect_params(self, request):
        '''
        @note: 校验支付回调后页面跳转回来的参数是否正常
        '''
        sign_in = request.REQUEST.get("sign", "")

        params = {}
        for key in ['result', 'out_trade_no', 'trade_no', 'request_token']:
            params[key] = request.REQUEST.get(key, "")

        params, prestr = self.format_params(params)
        sign = self.build_mysign(prestr)

        return sign == sign_in

    def validate_notify_params(self, request):
        '''
        @note: 校验支付通知接口的参数是否正常
        '''
        sign_in = request.REQUEST.get("sign", "")

        # 通知接口参数签名比较特殊，参数顺序是固定的
        prestr = ''
        for key in ['service', 'v', 'sec_id', 'notify_data']:
            value = smart_str(request.REQUEST.get(key, ""), self.input_charset)
            prestr += '%s=%s&' % (key, value)
        prestr = prestr[:-1]
        sign = self.build_mysign(prestr)

        return sign == sign_in


if __name__ == '__main__':
    alipay = Alipay()
    # print alipay.get_token(subject=u"心愿洗车行洗车服务", out_trade_no=u"W2014120815441258305", total_fee="20.00", out_user="f762a6f5d2b711e39a09685b35d0bf16")
    # print alipay.get_pay_url()

    class DATA(object):

        def __init__(self, data={}):
            self.REQUEST = data
            self.POST = data
            self.GET = data

    print alipay.validate_notify_params(DATA(data=dict(service="alipay.wap.trade.create.direct", v=2.0, sec_id=0001, notify_data="<notify >...</notify>")))
