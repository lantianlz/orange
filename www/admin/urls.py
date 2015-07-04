# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.admin.views',
                       url(r'^$', 'home'),
                       )

# 用户
urlpatterns += patterns('www.admin.views_user',

                        url(r'^user/user$', 'user'),
                        )
