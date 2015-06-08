# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.admin.views',
                       url(r'^$', 'home'),
                       )

# 用户
urlpatterns += patterns('www.admin.views_user',

                        url(r'^user/user/change_pwd$', 'change_pwd'),
                        url(r'^user/user/add_user$', 'add_user'),
                        url(r'^user/user/get_user_by_nick$', 'get_user_by_nick'),
                        url(r'^user/user/modify_user$', 'modify_user'),
                        url(r'^user/user/get_user_by_id$', 'get_user_by_id'),
                        url(r'^user/user/search$', 'search'),
                        url(r'^user/user$', 'user'),
                        )


# 站外登录用户管理
urlpatterns += patterns('www.admin.views_external_user',

                        url(r'^user/external/search$', 'get_external'),
                        url(r'^user/external$', 'external'),
                        )


# 权限
urlpatterns += patterns('www.admin.views_permission',

                        url(r'^permission/cancel_admin$', 'cancel_admin'),
                        url(r'^permission/save_user_permission$', 'save_user_permission'),
                        url(r'^permission/get_user_permissions$', 'get_user_permissions'),
                        url(r'^permission/get_all_administrators$', 'get_all_administrators'),
                        url(r'^permission$', 'permission'),
                        )

# 洗车行
urlpatterns += patterns('www.admin.views_car_wash',
                        url(r'^car_wash/car_wash/get_car_washs_by_name$', 'get_car_washs_by_name'),
                        url(r'^car_wash/car_wash/add_car_wash$', 'add_car_wash'),
                        url(r'^car_wash/car_wash/modify_car_wash$', 'modify_car_wash'),
                        url(r'^car_wash/car_wash/get_car_wash_by_id$', 'get_car_wash_by_id'),
                        url(r'^car_wash/car_wash/search$', 'search'),
                        url(r'^car_wash/car_wash$', 'car_wash'),
                        )

# 洗车行服务类型
urlpatterns += patterns('www.admin.views_service_type',
                        url(r'^car_wash/service_type/add_service_type$', 'add_service_type'),
                        url(r'^car_wash/service_type/modify_service_type$', 'modify_service_type'),
                        url(r'^car_wash/service_type/get_service_type_by_id$', 'get_service_type_by_id'),
                        url(r'^car_wash/service_type/search$', 'search'),
                        url(r'^car_wash/service_type$', 'service_type'),
                        )

# 洗车行服务价格
urlpatterns += patterns('www.admin.views_service_price',
                        url(r'^car_wash/service_price/remove_service_price$', 'remove_service_price'),
                        url(r'^car_wash/service_price/add_service_price$', 'add_service_price'),
                        url(r'^car_wash/service_price/modify_service_price$', 'modify_service_price'),
                        url(r'^car_wash/service_price/get_service_price_by_id$', 'get_service_price_by_id'),
                        url(r'^car_wash/service_price/search$', 'search'),
                        url(r'^car_wash/service_price$', 'service_price'),
                        )

# 洗车行银行信息
urlpatterns += patterns('www.admin.views_car_wash_bank',
                        url(r'^car_wash/bank/add_bank$', 'add_bank'),
                        url(r'^car_wash/bank/modify_bank$', 'modify_bank'),
                        url(r'^car_wash/bank/get_bank_by_id$', 'get_bank_by_id'),
                        url(r'^car_wash/bank/search$', 'search'),
                        url(r'^car_wash/bank$', 'bank'),
                        )

# 洗车行管理员
urlpatterns += patterns('www.admin.views_car_wash_manager',
                        url(r'^car_wash/manager/delete_manager$', 'delete_manager'),
                        url(r'^car_wash/manager/add_manager$', 'add_manager'),
                        url(r'^car_wash/manager/modify_manager$', 'modify_manager'),
                        url(r'^car_wash/manager/get_manager_by_id$', 'get_manager_by_id'),
                        url(r'^car_wash/manager/search$', 'search'),
                        url(r'^car_wash/manager$', 'manager'),
                        )

# 城市
urlpatterns += patterns('www.admin.views_city',

                        url(r'^city/city/get_citys_by_name$', 'get_citys_by_name'),
                        url(r'^city/city/get_districts_by_city$', 'get_districts_by_city'),
                        url(r'^city/city/modify_note$', 'modify_note'),
                        url(r'^city/city/modify_city$', 'modify_city'),
                        url(r'^city/city/get_city_by_id$', 'get_city_by_id'),
                        url(r'^city/city/search$', 'search'),
                        url(r'^city/city$', 'city'),
                        )

# 区
urlpatterns += patterns('www.admin.views_district',

                        url(r'^city/district/modify_district$', 'modify_district'),
                        url(r'^city/district/get_district_by_id$', 'get_district_by_id'),
                        url(r'^city/district/search$', 'search'),
                        url(r'^city/district$', 'district'),
                        )

# 统计
urlpatterns += patterns('www.admin.views_statistics',

                        url(r'^statistics/get_chart_data$', 'get_chart_data'),
                        url(r'^statistics/chart$', 'chart'),
                        url(r'^statistics/retention$', 'retention'),
                        url(r'^statistics/get_active_user$', 'get_active_user'),
                        url(r'^statistics/active_user$', 'active_user'),
                        )

# 缓存管理
urlpatterns += patterns('www.admin.views_caches',
                        
                        url(r'^tools/caches/get_cache$', 'get_cache'),
                        url(r'^tools/caches/remove_cache$', 'remove_cache'),
                        url(r'^tools/caches/modify_cache$', 'modify_cache'),
                        url(r'^tools/caches$', 'caches'),
                        )

# 缓存管理
urlpatterns += patterns('www.admin.views_sensitive_operation_log',

                        url(r'^tools/get_sensitive_operation_log$', 'get_sensitive_operation_log'),
                        url(r'^tools/sensitive_operation_log$', 'sensitive_operation_log'),
                        )

# 优惠券
urlpatterns += patterns('www.admin.views_coupon',

                        url(r'^coupon/modify_coupon$', 'modify_coupon'),
                        url(r'^coupon/get_coupon_by_id$', 'get_coupon_by_id'),
                        url(r'^coupon/search$', 'search'),
                        url(r'^coupon/add_coupon$', 'add_coupon'),
                        url(r'^coupon$', 'coupon'),
                        )

# 用户现金管理
urlpatterns += patterns('www.admin.views_user_cash_record',

                        url(r'^cash/user_cash_record/add_record$', 'add_record'),
                        url(r'^cash/user_cash_record/search$', 'search'),
                        url(r'^cash/user_cash_record$', 'user_cash_record'),
                        )

# 洗车行现金管理
urlpatterns += patterns('www.admin.views_car_wash_cash_record',

                        url(r'^cash/car_wash_cash_record/search_balance$', 'search_balance'),
                        url(r'^cash/car_wash_cash_record/add_record$', 'add_record'),
                        url(r'^cash/car_wash_cash_record/search$', 'search'),
                        url(r'^cash/car_wash_cash_record$', 'car_wash_cash_record'),
                        )

# 订单管理
urlpatterns += patterns('www.admin.views_order',

                        url(r'^order/get_order_by_id$', 'get_order_by_id'),
                        url(r'^order/search$', 'search'),
                        url(r'^order$', 'order'),
                        )


# 洗车码管理
urlpatterns += patterns('www.admin.views_order_code',

                        url(r'^order_code/get_code_by_id$', 'get_code_by_id'),
                        url(r'^order_code/search$', 'search'),
                        url(r'^order_code$', 'order_code'),
                        )

# 公司管理
urlpatterns += patterns('www.admin.views_company',
                        url(r'^company/company/get_companys_by_name$', 'get_companys_by_name'),
                        url(r'^company/company/modify_company$', 'modify_company'),
                        url(r'^company/company/add_company$', 'add_company'),
                        url(r'^company/company/get_company_by_id$', 'get_company_by_id'),
                        url(r'^company/company/search$', 'search'),
                        url(r'^company/company$', 'company'),
                        )

# 公司管理员
urlpatterns += patterns('www.admin.views_company_manager',
                        url(r'^company/manager/delete_manager$', 'delete_manager'),
                        url(r'^company/manager/add_manager$', 'add_manager'),
                        url(r'^company/manager/modify_manager$', 'modify_manager'),
                        url(r'^company/manager/get_manager_by_id$', 'get_manager_by_id'),
                        url(r'^company/manager/search$', 'search'),
                        url(r'^company/manager$', 'manager'),
                        )

# 公司旗下洗车行服务价格管理
urlpatterns += patterns('www.admin.views_company_batch_price',
                        url(r'^company/batch_price/save_price$', 'save_price'),
                        url(r'^company/batch_price$', 'batch_price'),
                        )

# 公司旗下洗车行服务价格管理
urlpatterns += patterns('www.admin.views_company_batch_info',
                        url(r'^company/batch_info/save_info$', 'save_info'),
                        url(r'^company/batch_info$', 'batch_info'),
                        )