# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.account.views',
                       url(r'^captcha$', 'captcha'),
                       url(r'^user_settings$', 'change_profile'),
                       url(r'^user_settings/change_pwd$', 'change_pwd'),
                       url(r'^user_settings/change_email$', 'change_email'),
                       url(r'^user_settings/verify_email$', 'verify_email'),

                       url(r'^get_user_info_by_id', 'get_user_info_by_id'),
                       url(r'^get_user_info_by_nick', 'get_user_info_by_nick'),
                       )

urlpatterns += patterns('www.account.views_oauth',
                        url(r'^oauth/weixin$', 'oauth_weixin'),
                        url(r'^oauth/qq$', 'oauth_qq'),
                        url(r'^oauth/sina$', 'oauth_sina'),
                        )
