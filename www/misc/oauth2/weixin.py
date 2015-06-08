# -*- coding: utf-8 -*-

'''
@author: lizheng
@date: 2014-01-01
'''
import requests
import urllib
import json
# import logging
# from pprint import pprint

from django.conf import settings

API_URL = 'https://api.weixin.qq.com'
REDIRECT_URI = '%s/account/oauth/weixin' % settings.MAIN_DOMAIN


class Consumer(object):

    def __init__(self, app_key, response_type='code'):
        from www.weixin.interface import dict_weixin_app

        self.client_id = dict_weixin_app[app_key]["app_id"]
        self.client_secret = dict_weixin_app[app_key]["app_secret"]
        self.api_url = API_URL
        self.response_type = response_type
        self.redirect_uri = urllib.quote_plus(REDIRECT_URI)
        self.state = 'home'
        self.grant_type = 'authorization_code'
        self.dict_format = dict(appid=self.client_id, client_secret=self.client_secret,
                                response_type=self.response_type, api_url=self.api_url, grant_type=self.grant_type,
                                redirect_uri=self.redirect_uri, state=self.state)

    def authorize(self):
        return ('https://open.weixin.qq.com/connect/oauth2/authorize?appid=%(appid)s'
                '&redirect_uri=%(redirect_uri)s&response_type=%(response_type)s&scope=snsapi_base&state=%(state)s#wechat_redirect') % self.dict_format

    def token(self, code):
        self.dict_format.update(dict(code=code))

        access_token_url = ('%(api_url)s/sns/oauth2/access_token?grant_type=%(grant_type)s&'
                            'appid=%(appid)s&secret=%(client_secret)s&code=%(code)s') % self.dict_format
        for i in range(3):
            try:
                rep = requests.get(access_token_url, timeout=5, verify=False)
                break
            except:
                pass

        content = rep.text
        dict_result = json.loads(content)
        return dict_result

    def refresh_token(self, refresh_token):
        pass

    def request_api(self, access_token, method_name, data={}, method='GET'):
        request_url = '%(api_url)s%(method_name)s' % dict(api_url=self.api_url, method_name=method_name)
        data.update(oauth_consumer_key=self.client_id)
        if method == 'GET':
            request_url = '%s?%s' % (request_url, urllib.urlencode(data))
            rep = requests.get(request_url, timeout=30, verify=False)
        else:
            rep = requests.post(request_url, data=data, timeout=30, verify=False)
        content = rep.content
        try:
            return json.loads(content)
        except:
            return content
