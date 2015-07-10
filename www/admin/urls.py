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

# 权限
urlpatterns += patterns('www.admin.views_permission',

	url(r'^permission/cancel_admin$', 'cancel_admin'),
	url(r'^permission/save_user_permission$', 'save_user_permission'),
	url(r'^permission/get_user_permissions$', 'get_user_permissions'),
	url(r'^permission/get_all_administrators$', 'get_all_administrators'),
	url(r'^permission$', 'permission'),
)