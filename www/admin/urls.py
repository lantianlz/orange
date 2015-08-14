# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.admin.views',
	url(r'^$', 'home'),
)

# 用户
urlpatterns += patterns('www.admin.views_user',

    url(r'^user/change_pwd$', 'change_pwd'),
    url(r'^user/add_user$', 'add_user'),
    url(r'^user/get_user_by_nick$', 'get_user_by_nick'),
    url(r'^user/modify_user$', 'modify_user'),
    url(r'^user/get_user_by_id$', 'get_user_by_id'),
    url(r'^user/search$', 'search'),
    url(r'^user$', 'user'),
)

# 公司管理
urlpatterns += patterns('www.admin.views_company',
    url(r'^company/get_companys_by_name$', 'get_companys_by_name'),
    url(r'^company/modify_company$', 'modify_company'),
    url(r'^company/add_company$', 'add_company'),
    url(r'^company/get_company_by_id$', 'get_company_by_id'),
    url(r'^company/search$', 'search'),
    url(r'^company$', 'company'),
)

# 公司管理员
urlpatterns += patterns('www.admin.views_company_manager',
    url(r'^company_manager/delete_manager$', 'delete_manager'),
    url(r'^company_manager/add_manager$', 'add_manager'),
    url(r'^company_manager/modify_manager$', 'modify_manager'),
    url(r'^company_manager/get_manager_by_id$', 'get_manager_by_id'),
    url(r'^company_manager/search$', 'search'),
    url(r'^company_manager$', 'company_manager'),
)

# 现金账户
urlpatterns += patterns('www.admin.views_cash_account',
    url(r'^cash_account/modify_cash_account$', 'modify_cash_account'),
    url(r'^cash_account/get_cash_account_by_id$', 'get_cash_account_by_id'),
    url(r'^cash_account/search$', 'search'),
    url(r'^cash_account$', 'cash_account'),
)

# 现金流水
urlpatterns += patterns('www.admin.views_cash_record',
    url(r'^cash_record/add_cash_account$', 'add_cash_record'),
    url(r'^cash_record/search$', 'search'),
    url(r'^cash_record$', 'cash_record'),
)

# 产品管理
urlpatterns += patterns('www.admin.views_item',

    url(r'^item/get_items_by_name$', 'get_items_by_name'),
    url(r'^item/add_item$', 'add_item'),
    url(r'^item/modify_item$', 'modify_item'),
    url(r'^item/get_item_by_id$', 'get_item_by_id'),
    url(r'^item/search$', 'search'),
    url(r'^item$', 'item'),
)

# 套餐管理
urlpatterns += patterns('www.admin.views_meal',

    url(r'^meal/get_meals_by_name$', 'get_meals_by_name'),
    url(r'^meal/add_meal$', 'add_meal'),
    url(r'^meal/modify_meal$', 'modify_meal'),
    url(r'^meal/get_meal_by_id$', 'get_meal_by_id'),
    url(r'^meal/search$', 'search'),
    url(r'^meal$', 'meal'),
)

# 订单管理
urlpatterns += patterns('www.admin.views_order',

    url(r'^purchase/print_purchase$', 'print_purchase'),
    url(r'^purchase/get_purchase$', 'get_purchase'),
    url(r'^purchase$', 'purchase'),

    url(r'^order/print_order$', 'print_order'),
    url(r'^order/add_order$', 'add_order'),
    url(r'^order/distribute_order$', 'distribute_order'),
    url(r'^order/confirm_order$', 'confirm_order'),
    url(r'^order/drop_order$', 'drop_order'),
    url(r'^order/get_order_by_id$', 'get_order_by_id'),
    url(r'^order/search$', 'search'),
    url(r'^order$', 'order'),
)

# 产品管理
urlpatterns += patterns('www.admin.views_booking',

    url(r'^booking/modify_booking$', 'modify_booking'),
    url(r'^booking/get_booking_by_id$', 'get_booking_by_id'),
    url(r'^booking/search$', 'search'),
    url(r'^booking$', 'booking'),
)

# 城市
urlpatterns += patterns('www.admin.views_city',

    url(r'^city/get_citys_by_name$', 'get_citys_by_name'),
    url(r'^city/get_districts_by_city$', 'get_districts_by_city'),
    url(r'^city/modify_note$', 'modify_note'),
    url(r'^city/modify_city$', 'modify_city'),
    url(r'^city/get_city_by_id$', 'get_city_by_id'),
    url(r'^city/search$', 'search'),
    url(r'^city$', 'city'),
)

# 区
urlpatterns += patterns('www.admin.views_district',

    url(r'^district/modify_district$', 'modify_district'),
    url(r'^district/get_district_by_id$', 'get_district_by_id'),
    url(r'^district/search$', 'search'),
    url(r'^district$', 'district'),
)

# 缓存管理
urlpatterns += patterns('www.admin.views_caches',

	url(r'^caches/get_cache$', 'get_cache'),
	url(r'^caches/remove_cache$', 'remove_cache'),
	url(r'^caches/modify_cache$', 'modify_cache'),
	url(r'^caches$', 'caches'),
)

# 敏感操作日志管理
urlpatterns += patterns('www.admin.views_sensitive_operation_log',

	url(r'^sensitive_operation_log/get_sensitive_operation_log$', 'get_sensitive_operation_log'),
	url(r'^sensitive_operation_log$', 'sensitive_operation_log'),
)

# 权限
urlpatterns += patterns('www.admin.views_permission',

	url(r'^permission/cancel_admin$', 'cancel_admin'),
	url(r'^permission/save_user_permission$', 'save_user_permission'),
	url(r'^permission/get_user_permissions$', 'get_user_permissions'),
	url(r'^permission/get_all_administrators$', 'get_all_administrators'),
	url(r'^permission$', 'permission'),
)