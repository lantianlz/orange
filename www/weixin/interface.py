# -*- coding: utf-8 -*-
import random
import string
import hashlib
import time
import requests
import json
import logging
from django.conf import settings
from pyquery import PyQuery as pq

from common import cache, debug
from www.misc import consts


dict_err = {
    70100: u'发送模板消息异常',
}
dict_err.update(consts.G_DICT_ERROR)


weixin_api_url = 'https://api.weixin.qq.com'
dict_weixin_app = {
    'orange_test': {
        'app_id': 'wx0d227d4f9b19658a',
        'app_secret': '513bdaf5b6022df4913f4cb5543fa688',
        'app_type': 'gh_65671b9fff9d',
        'token': 'orange_test',
        'url': ''
    },
    'orange': {
        'app_id': 'wxd6922b078dff1607',
        'app_secret': '',
        'app_type': 'gh_6830b9f3748d',
        'token': 'orange',
        'url': ''
    },
}


class WeixinBase(object):

    def __init__(self):
        self.cache = cache.Cache()

    def __del__(self):
        del self.cache

    def init_app_key(self, default_value="orange"):
        return "orange_test" if settings.LOCAL_FLAG else default_value

    def get_base_text_response(self):
        '''
        @note: 文字信息模板
        '''
        return u'''
        <xml>
        <ToUserName><![CDATA[%(to_user)s]]></ToUserName>
        <FromUserName><![CDATA[%(from_user)s]]></FromUserName>
        <CreateTime>%(timestamp)s</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[%(content)s]]></Content>
        </xml>
        '''

    def get_base_news_response(self, items=None):
        '''
        @note: 图文信息模板
        '''
        return u'''
        <xml>
        <ToUserName><![CDATA[%(to_user)s]]></ToUserName>
        <FromUserName><![CDATA[%(from_user)s]]></FromUserName>
        <CreateTime>%(timestamp)s</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>%(articles_count)s</ArticleCount>
        <Articles>
        ''' + (items or self.get_base_news_item_response()) + \
            '''
        </Articles>
        </xml>
        '''

    def get_base_news_item_response(self):
        return u'''
        <item>
        <Title><![CDATA[%(title)s]]></Title>
        <Description><![CDATA[%(des)s]]></Description>
        <PicUrl><![CDATA[%(picurl)s]]></PicUrl>
        <Url><![CDATA[%(hrefurl)s]]></Url>
        </item>
        '''

    def get_base_content_response(self, to_user, from_user, content):
        base_xml = self.get_base_text_response()
        return base_xml % dict(to_user=from_user, from_user=to_user, timestamp=int(time.time()), content=content)

    def get_error_response(self, to_user, from_user, error_info):
        base_xml = self.get_base_text_response()
        return base_xml % dict(to_user=from_user, from_user=to_user, timestamp=int(time.time()), content=error_info)

    def get_subscribe_event_response(self, to_user, from_user):
        content = (u'三点十分，下午茶点服务专家；'
                   u'我们专注于为企业提供按需定制的下午茶点服务，免费配送上门。\n'
                   u'新鲜的水果，可口的点心，尽在三点十分，欢迎立即免费试吃体验。'
                   )
        return self.get_base_content_response(to_user, from_user, content=content)

    def get_customer_service_response(self, to_user, from_user):
        return u'''
        <xml>
        <ToUserName><![CDATA[%(to_user)s]]></ToUserName>
        <FromUserName><![CDATA[%(from_user)s]]></FromUserName>
        <CreateTime>%(timestamp)s</CreateTime>
        <MsgType><![CDATA[transfer_customer_service]]></MsgType>
        </xml>
        ''' % dict(to_user=from_user, from_user=to_user, timestamp=int(time.time()))

    def format_input_xml(self, xml):
        '''
        @note: 标签替换为小写，以便pyquery能识别
        '''
        for key in ['ToUserName>', 'FromUserName>', 'CreateTime>', 'MsgType>', 'Content>', 'MsgId>', 'PicUrl>',
                    'MediaId>', 'Format>', 'ThumbMediaId>', 'Event>', 'EventKey>', 'Ticket>', 'Recognition>',
                    'DeviceID>', 'SessionID>', 'DeviceType>', 'OpenID>']:
            xml = xml.replace(key, key.lower())
        return xml

    def get_response(self, xml):
        from www.account.interface import UserBase

        xml = self.format_input_xml(xml)
        jq = pq(xml)
        to_user = jq('tousername')[0].text
        from_user = jq('fromusername')[0].text
        events = jq('event')
        app_key = self.get_app_key_by_app_type(to_user)
        logging.error(u'收到一个来自app：%s 的请求' % app_key)

        if "test" in app_key:   # 剔除测试公众号发送信息
            return

        # 事件
        if events:
            event = events[0].text.lower()
            if event in ('scan', 'subscribe'):  # 扫码登陆事件
                tickets = jq('ticket')
                if tickets:
                    ticket = tickets[0].text
                    errcode, errmsg = UserBase().login_by_weixin_qr_code(ticket, from_user, app_key)
                    return self.get_base_content_response(to_user, from_user, errmsg)
            if event in ('subscribe',):
                # pass

                # 发送客服消息通知用户
                content = u"所推荐的公司成功订购后，有红包相送哦"
                url = u'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxd6922b078dff1607&redirect_uri=http%3A%2F%2Fwww.3-10.cc%2Faccount%2Foauth%2Fweixin&response_type=code&scope=snsapi_base&state=recommend#wechat_redirect'
                img_info = u'[{"title": "推荐有礼", "description": "%s", "url": "%s", "picurl": "%s"}]' \
                    % (content, url, 'http://static.3-10.cc/img/recommend.jpg')
                self.send_msg_to_weixin(content, from_user, app_key, msg_type='news', img_info=img_info)

                return self.get_subscribe_event_response(to_user, from_user)
            elif event in ('click', ):
                event_key = jq('eventkey')[0].text.lower()
                if event_key == 'feedback':
                    content = (u'欢迎小伙伴们踊跃反馈意见，你的意见一经采纳，必有好礼相送。\n'
                               u'反馈方法：直接在此微信服务号中输入你的金玉良言即可，客服人员会及时跟进哦'
                               )
                    return self.get_base_content_response(to_user, from_user, content=content)

        # 文字识别
        msg_types = jq('msgtype')
        if msg_types:
            msg_type = msg_types[0].text
            if msg_type == 'text':
                content = jq('content')[0].text.strip()
                logging.error(u'收到用户发送的文本数据，内容如下：%s' % content)
                return self.get_customer_service_response(to_user, from_user)   # 多客服接管

    def get_app_key_by_app_type(self, app_type):
        for key in dict_weixin_app:
            if dict_weixin_app[key]['app_type'] == app_type:
                return key
        raise Exception, u'app_key not found by: %s' % app_type

    def send_msg_to_weixin(self, content, to_user, app_key, msg_type='text', img_info=''):
        '''
        @note: 发送信息给微信
        '''
        # json的dumps字符串中中文微信不识别，修改为直接构造
        if msg_type == 'text':
            data = u'{"text": {"content": "%s"}, "msgtype": "%s", "touser": "%s"}' % (content, msg_type, to_user)
        else:
            data = u'{"news":{"articles": %s}, "msgtype":"%s", "touser": "%s"}' % (img_info, msg_type, to_user)

        data = data.encode('utf8')

        access_token = self.get_weixin_access_token(app_key)
        url = '%s/cgi-bin/message/custom/send?access_token=%s' % (weixin_api_url, access_token)

        for i in range(3):
            try:
                r = requests.post(url, data=data, timeout=5, verify=False)
                break
            except:
                pass

        r.raise_for_status()
        content = json.loads(r.content)
        logging.error('send msg to weixin resp is %s' % (content,))

    def get_weixin_access_token(self, app_key):
        # 本地调试模式不走缓存
        if not settings.LOCAL_FLAG:
            key = 'weixin_access_token_for_%s' % app_key
            access_token = self.cache.get(key)
            if access_token is None:
                access_token, expires_in = self.get_weixin_access_token_directly(app_key)
                if access_token:
                    self.cache.set(key, access_token, int(expires_in))
        else:
            access_token, expires_in = self.get_weixin_access_token_directly(app_key)
        return access_token

    def get_weixin_access_token_directly(self, app_key):
        access_token, expires_in = '', 0
        content = ''
        url = '%s/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (weixin_api_url, dict_weixin_app[app_key]['app_id'],
                                                                                    dict_weixin_app[app_key]['app_secret'])
        try:
            r = requests.get(url, timeout=20, verify=False)
            content = r.content
            r.raise_for_status()
            content = json.loads(content)
            access_token = content['access_token']
            expires_in = content['expires_in']
        except Exception, e:
            logging.error(u'get_weixin_access_token rep is %s' % content)
            debug.get_debug_detail(e)
        assert access_token
        return access_token, expires_in

    def get_user_info(self, app_key, openid):
        """
        @note: 获取一关注公众号的用户信息
        """
        access_token = self.get_weixin_access_token(app_key)
        url = '%s/cgi-bin/user/info?access_token=%s&openid=%s' % (weixin_api_url, access_token, openid)
        data = {}
        try:
            r = requests.get(url, timeout=20, verify=False)
            text = r.text
            r.raise_for_status()
            data = json.loads(text)
            if data.get("errmsg") or data.get("subscribe") == 0:
                logging.error("error user info data is:%s" % data)
                data = {}
        except Exception, e:
            debug.get_debug_detail_and_send_email(e)
        return data

    def get_qr_code_ticket(self, app_key, expire=300):
        """
        @note: 获取二维码对应的ticket
        """
        access_token = self.get_weixin_access_token(app_key)
        url = '%s/cgi-bin/qrcode/create?access_token=%s' % (weixin_api_url, access_token)
        data = u'{"expire_seconds":%s, "action_name":"QR_SCENE", "action_info": {"scene": {"scene_id": %s}}' % (expire, int(time.time() * 1000))
        data = data.encode('utf8')

        result = {}
        try:
            r = requests.post(url, data=data, timeout=20, verify=False)
            text = r.text
            r.raise_for_status()
            result = json.loads(text)
            if result.get("errmsg") or result.get("subscribe") == 0:
                logging.error("error create_qr_code result is:%s" % result)
                result = {}
        except Exception, e:
            debug.get_debug_detail(e)
        return result

    def send_template_msg(self, app_key, openid, content, template_id, jump_url=''):
        """
        @note: 发送模板消息
        """
        access_token = self.get_weixin_access_token(app_key)
        url = '%s/cgi-bin/message/template/send?access_token=%s' % (weixin_api_url, access_token)

        data = u'''
        {
           "touser":"%(openid)s",
           "template_id":"%(template_id)s",
           "url":"%(jump_url)s",
           "data":%(content)s
       }
       ''' % dict(openid=openid, template_id=template_id, jump_url=jump_url, content=content)
        data = data.encode('utf8')

        errcode, errmsg = 0, dict_err.get(0)
        try:
            r = requests.post(url, data=data, timeout=20, verify=False)
            text = r.text
            r.raise_for_status()
            result = json.loads(text)
            errcode, errmsg = result["errcode"], result["errmsg"]
        except Exception, e:
            debug.get_debug_detail(e)
            errcode, errmsg = 70100, dict_err.get(70100)
        return errcode, errmsg

    def send_buy_success_template_msg(self, openid, name, remark, app_key=None):
        template_id = "xZssRUhtE-xGOINN1eVaVpoprKtmQq9VOqcPFkujCL0"
        app_key = app_key or self.init_app_key()
        content = u'''
         {
            "name": {
                "value":"%(name)s",
                "color":"#EF8A55"
            },
            "remark":{
                "value":"%(remark)s",
                "color":"#999999"
            }
         }
        ''' % dict(name=name, remark=remark)

        return self.send_template_msg(app_key, openid, content, template_id)

    def send_use_order_code_template_msg(self, openid, product_type, name, time, remark, app_key=None):
        template_id = "gdkyj2dncX-KXtPFYIArByLiSs00bq2wfNBru8fxeXg"
        app_key = app_key or self.init_app_key()
        content = u'''
         {
            "productType": {
                "value":"%(product_type)s",
                "color":"#000000"
            },
            "name": {
                "value":"%(name)s",
                "color":"#000000"
            },
            "time":{
                "value":"%(time)s",
                "color":"#000000"
            },
            "remark":{
                "value":"%(remark)s",
                "color":"#EF8A55"
            }
         }
        ''' % dict(product_type=product_type, name=name, time=time, remark=remark)

        return self.send_template_msg(app_key, openid, content, template_id)

    def send_balance_insufficient_template_msg(self, openid, info, name, balance, remark, app_key=None):
        '''
        发送余额不足通知
        '''
        template_id = "uw0DFAED4ajczOZVUNHPAz3BKtSlgb8NUcb4F8FtEIc"
        app_key = app_key or self.init_app_key()
        content = u'''
         {
            "first": {
                "value":"%(info)s",
                "color":"#EF7B32"
            },
            "keyword1": {
                "value":"%(name)s",
                "color":"#000000"
            },
            "keyword2":{
                "value":"%(balance)s",
                "color":"#000000"
            },
            "remark":{
                "value":"%(remark)s",
                "color":"#000000"
            }
         }
        ''' % dict(info=info, name=name, balance=balance, remark=remark)

        return self.send_template_msg(app_key, openid, content, template_id)

    def send_recharge_success_template_msg(self, openid, info, date, amount, remark, app_key=None):
        '''
        发送充值成功通知
        '''
        template_id = "r2u4sOmPKAyQPCz5nfIjwrodnJ9mpNxRTTrTe_8B_x0"
        app_key = app_key or self.init_app_key()
        content = u'''
         {
            "first": {
                "value":"%(info)s",
                "color":"#EF7B32"
            },
            "keynote1": {
                "value":"%(date)s",
                "color":"#000000"
            },
            "keynote2":{
                "value":"%(amount)s",
                "color":"#000000"
            },
            "remark":{
                "value":"%(remark)s",
                "color":"#000000"
            }
         }
        ''' % dict(info=info, date=date, amount=amount, remark=remark)

        return self.send_template_msg(app_key, openid, content, template_id)

    def send_todo_list_template_msg(self, openid, info, job, priority, remark, app_key=None):
        '''
        发送待办任务提醒通知
        '''
        template_id = "-rAhCPV9q3lUoslRYQUlHhpwvJXraX7BDuJgfKW2Bss"
        app_key = app_key or self.init_app_key()
        content = u'''
         {
            "first": {
                "value":"%(info)s",
                "color":"#EF7B32"
            },
            "keyword1": {
                "value":"%(job)s",
                "color":"#000000"
            },
            "keyword2":{
                "value":"%(priority)s",
                "color":"#000000"
            },
            "remark":{
                "value":"%(remark)s",
                "color":"#000000"
            }
         }
        ''' % dict(info=info, job=job, priority=priority, remark=remark)

        return self.send_template_msg(app_key, openid, content, template_id)

    def get_weixin_jsapi_ticket(self, app_key):
        # 本地调试模式不走缓存
        if not settings.LOCAL_FLAG:
            key = 'weixin_jsapi_ticket_for_%s' % app_key
            ticket = self.cache.get(key)
            if ticket is None:
                ticket, expires_in = self.get_weixin_jsapi_ticket_directly(app_key)
                if ticket:
                    self.cache.set(key, ticket, int(expires_in))
        else:
            ticket, expires_in = self.get_weixin_jsapi_ticket_directly(app_key)
        return ticket

    def get_weixin_jsapi_ticket_directly(self, app_key):
        ticket, expires_in = '', 0
        content = ''

        url = '%s/cgi-bin/ticket/getticket?access_token=%s&type=jsapi' % (weixin_api_url, self.get_weixin_access_token(app_key))
        try:
            r = requests.get(url, timeout=20, verify=False)
            content = r.content
            r.raise_for_status()
            content = json.loads(content)
            ticket = content['ticket']
            expires_in = content['expires_in']
        except Exception, e:
            logging.error(u'get_weixin_jsapi_ticket rep is %s' % content)
            debug.get_debug_detail(e)
        assert ticket
        return ticket, expires_in


class Sign(object):

    def __init__(self, jsapi_ticket, url):
        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret
