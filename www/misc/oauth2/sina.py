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

CLIENT_ID = '504150080'
CLIENT_SECRET = '256233cbef121082ad9c77297cf90fb3'
API_URL = 'https://api.weibo.com'
REDIRECT_URI = '%s/account/oauth/sina' % settings.MAIN_DOMAIN


class Consumer(object):

    def __init__(self, response_type='code'):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.api_url = API_URL
        self.response_type = response_type
        self.redirect_uri = REDIRECT_URI  # urllib.quote_plus(REDIRECT_URI)
        self.grant_type = 'authorization_code'
        self.dict_format = dict(client_id=self.client_id, client_secret=self.client_secret,
                                response_type=self.response_type, api_url=self.api_url, grant_type=self.grant_type,
                                redirect_uri=self.redirect_uri)

    def authorize(self):
        return ('%(api_url)s/oauth2/authorize?response_type=%(response_type)s&client_id=%(client_id)s'
                '&redirect_uri=%(redirect_uri)s') % self.dict_format

    def token(self, code):
        self.dict_format.update(dict(code=code))
        access_token_url = ('%(api_url)s/oauth2/access_token') % self.dict_format
        data = dict(grant_type=self.dict_format['grant_type'],
                    client_id=self.dict_format['client_id'],
                    client_secret=self.dict_format['client_secret'],
                    code=self.dict_format['code'],
                    redirect_uri=self.dict_format['redirect_uri'],
                    )
        rep = requests.post(access_token_url, data=data, timeout=30)
        content = rep.text
        dict_result = json.loads(content)
        return dict(access_token=dict_result['access_token'], expires_in=dict_result['expires_in'],
                    uid=dict_result['uid'], refresh_token='')

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
