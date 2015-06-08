# -*- coding: utf-8 -*-

'''
@author: lizheng
@date: 2014-01-01
'''
import requests
import urllib
import re
import json
from pprint import pprint

from django.conf import settings

CLIENT_ID = '101147045'
CLIENT_SECRET = 'af3833620eec38c3177365195325e177'
API_URL = 'https://graph.qq.com'
REDIRECT_URI = '%s/account/oauth/qq' % settings.MAIN_DOMAIN


class Consumer(object):

    def __init__(self, response_type='code'):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.api_url = API_URL
        self.response_type = response_type
        self.redirect_uri = urllib.quote_plus(REDIRECT_URI)
        self.state = 'orange_state'
        self.grant_type = 'authorization_code'
        self.dict_format = dict(client_id=self.client_id, client_secret=self.client_secret,
                                response_type=self.response_type, api_url=self.api_url, grant_type=self.grant_type,
                                redirect_uri=self.redirect_uri, state=self.state)

    def authorize(self):
        return ('%(api_url)s/oauth2.0/authorize?response_type=%(response_type)s&client_id=%(client_id)s'
                '&redirect_uri=%(redirect_uri)s&state=%(state)s') % self.dict_format

    def token(self, code):
        self.dict_format.update(dict(code=code))
        access_token_url = ('%(api_url)s/oauth2.0/token?grant_type=%(grant_type)s&'
                            'client_id=%(client_id)s&client_secret=%(client_secret)s&code=%(code)s'
                            '&state=%(state)s&redirect_uri=%(redirect_uri)s') % self.dict_format

        rep = requests.get(access_token_url, timeout=30)
        content = rep.text
        dict_result = {}
        if 'access_token=' in content:
            for r in content.split('&'):
                dict_result.update({r.split('=')[0]: r.split('=')[1]})
        return dict_result

    def refresh_token(self, refresh_token):
        pass

    def request_api(self, access_token, method_name, data={}, method='GET'):
        request_url = '%(api_url)s%(method_name)s' % dict(api_url=self.api_url, method_name=method_name)
        data.update(oauth_consumer_key=self.client_id)
        if method == 'GET':
            request_url = '%s?%s' % (request_url, urllib.urlencode(data))
            rep = requests.get(request_url, timeout=30)
        else:
            rep = requests.post(request_url, data=data, timeout=30)
        content = rep.content
        # print request_url
        # print content
        try:
            return json.loads(content)
        except:
            return content

    def get_openid(self, access_token):
        content = self.request_api(access_token, '/oauth2.0/me', data=dict(access_token=access_token))
        openid = ''
        if 'openid' in content:
            re_str = u'"openid":"(.+)"'
            openids = re.findall(re_str, content)
            if openids:
                openid = openids[0]
        return openid
