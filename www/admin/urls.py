# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
# from django.conf import settings

urlpatterns = patterns('www.admin.views',
    url(r'^$', 'home'),
    url(r'^nav$', 'nav'),
)

# 注册用户管理
urlpatterns += patterns('www.admin.views_user',

    url(r'^user/change_pwd$', 'change_pwd'),
    url(r'^user/add_user$', 'add_user'),
    url(r'^user/get_user_by_nick$', 'get_user_by_nick'),
    url(r'^user/modify_user$', 'modify_user'),
    url(r'^user/get_user_by_id$', 'get_user_by_id'),
    url(r'^user/search$', 'search'),
    url(r'^user$', 'user'),
)

# 销售人员管理
urlpatterns += patterns('www.admin.views_sale_man',

    url(r'^sale_man/add_sale_man$', 'add_sale_man'),
    url(r'^sale_man/modify_sale_man$', 'modify_sale_man'),
    url(r'^sale_man/get_sale_man_by_id$', 'get_sale_man_by_id'),
    url(r'^sale_man/search$', 'search'),
    url(r'^sale_man$', 'sale_man'),
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

# 公司现金账户
urlpatterns += patterns('www.admin.views_cash_account',

    url(r'^cash_account/modify_cash_account$', 'modify_cash_account'),
    url(r'^cash_account/get_cash_account_by_id$', 'get_cash_account_by_id'),
    url(r'^cash_account/search$', 'search'),
    url(r'^cash_account$', 'cash_account'),
)

# 公司现金流水
urlpatterns += patterns('www.admin.views_cash_record',

    url(r'^cash_record/change_is_invoice$', 'change_is_invoice'),
    url(r'^cash_record/add_cash_account$', 'add_cash_record'),
    url(r'^cash_record/search$', 'search'),
    url(r'^cash_record$', 'cash_record'),
)

# 供货商管理
urlpatterns += patterns('www.admin.views_supplier',

    url(r'^supplier/get_suppliers_by_name$', 'get_suppliers_by_name'),
    url(r'^supplier/modify_supplier$', 'modify_supplier'),
    url(r'^supplier/add_supplier$', 'add_supplier'),
    url(r'^supplier/get_supplier_by_id$', 'get_supplier_by_id'),
    url(r'^supplier/search$', 'search'),
    url(r'^supplier$', 'supplier'),
)

# 供货商现金账户
urlpatterns += patterns('www.admin.views_supplier_cash_account',

    url(r'^supplier_cash_account/search$', 'search'),
    url(r'^supplier_cash_account$', 'supplier_cash_account'),
)

# 供货商现金流水
urlpatterns += patterns('www.admin.views_supplier_cash_record',

    url(r'^supplier_cash_record/add_supplier_cash_account$', 'add_supplier_cash_record'),
    url(r'^supplier_cash_record/search$', 'search'),
    url(r'^supplier_cash_record$', 'supplier_cash_record'),
)

# 产品管理
urlpatterns += patterns('www.admin.views_item',
    
    url(r'^item/get_item_types$', 'get_item_types'),
    url(r'^item/get_items_by_name$', 'get_items_by_name'),
    url(r'^item/get_items_by_name_for_combox$', 'get_items_by_name_for_combox'),
    url(r'^item/add_item$', 'add_item'),
    url(r'^item/modify_item$', 'modify_item'),
    url(r'^item/get_item_by_id$', 'get_item_by_id'),
    url(r'^item/search$', 'search'),
    url(r'^item$', 'item'),
)

# 套餐管理
urlpatterns += patterns('www.admin.views_meal',

    url(r'^meal/get_items_of_meal', 'get_items_of_meal'),
    url(r'^meal/get_meals_by_name$', 'get_meals_by_name'),
    url(r'^meal/add_meal$', 'add_meal'),
    url(r'^meal/modify_meal$', 'modify_meal'),
    url(r'^meal/get_meal_by_id$', 'get_meal_by_id'),
    url(r'^meal/search$', 'search'),
    url(r'^meal$', 'meal'),
)

# 水果价格管理
urlpatterns += patterns('www.admin.views_fruit_price',

    url(r'^fruit_price/modify_fruit_price$', 'modify_fruit_price'),
    url(r'^fruit_price$', 'fruit_price'),
)

# 订单管理
urlpatterns += patterns('www.admin.views_order',

    url(r'^order/order_state$', 'order_state'),
    url(r'^order/get_items_of_order', 'get_items_of_order'),
    url(r'^order/print_order$', 'print_order'),
    url(r'^order/modify_order$', 'modify_order'),
    url(r'^order/add_order$', 'add_order'),
    url(r'^order/distribute_order$', 'distribute_order'),
    url(r'^order/confirm_order$', 'confirm_order'),
    url(r'^order/drop_order$', 'drop_order'),
    url(r'^order/get_order_by_id$', 'get_order_by_id'),
    url(r'^order/search$', 'search'),
    url(r'^create_order$', 'create_order'),
    url(r'^order$', 'order'),
)

# 采购汇总
urlpatterns += patterns('www.admin.views_purchase',

    url(r'^purchase/print_purchase$', 'print_purchase'),
    url(r'^purchase/get_purchase$', 'get_purchase'),
    url(r'^purchase$', 'purchase'),
)

# 采购流水
urlpatterns += patterns('www.admin.views_purchase_record',

    url(r'^purchase_record/modify_record$', 'modify_record'),
    url(r'^purchase_record/add_record$', 'add_record'),
    url(r'^purchase_record/get_record_by_id$', 'get_record_by_id'),
    url(r'^purchase_record/search$', 'search'),
    url(r'^purchase_record$', 'purchase_record'),
)

# 采购对账
urlpatterns += patterns('www.admin.views_purchase_statement',

    url(r'^purchase_statement/get_purchase_statement$', 'get_purchase_statement'),
    url(r'^purchase_statement$', 'purchase_statement'),
)

# 预订管理
urlpatterns += patterns('www.admin.views_booking',

    url(r'^booking/modify_booking$', 'modify_booking'),
    url(r'^booking/get_booking_by_id$', 'get_booking_by_id'),
    url(r'^booking/search$', 'search'),
    url(r'^booking$', 'booking'),
)

# 发票
urlpatterns += patterns('www.admin.views_invoice',

    url(r'^invoice/modify_invoice$', 'modify_invoice'),
    url(r'^invoice/add_invoice$', 'add_invoice'),
    url(r'^invoice/get_invoice_by_id$', 'get_invoice_by_id'),
    url(r'^invoice/get_invoice_by_company_id$', 'get_invoice_by_company_id'),
    url(r'^invoice/search$', 'search'),
    url(r'^invoice$', 'invoice'),
)

# 发票记录
urlpatterns += patterns('www.admin.views_invoice_record',

    url(r'^invoice_record/modify_record$', 'modify_record'),
    url(r'^invoice_record/add_record$', 'add_record'),
    url(r'^invoice_record/get_record_by_id$', 'get_record_by_id'),
    url(r'^invoice_record/search$', 'search'),
    url(r'^invoice_record$', 'invoice_record'),
)

# 发票对账
urlpatterns += patterns('www.admin.views_invoice_statement',

    url(r'^invoice_statement/get_invoice_statement$', 'get_invoice_statement'),
    url(r'^invoice_statement$', 'invoice_statement'),
)

# 库存产品
urlpatterns += patterns('www.admin.views_inventory',

    url(r'^inventory/modify_inventory$', 'modify_inventory'),
    url(r'^inventory/add_inventory$', 'add_inventory'),
    url(r'^inventory/get_inventory_by_id$', 'get_inventory_by_id'),
    url(r'^inventory/get_inventorys_by_name$', 'get_inventorys_by_name'),
    url(r'^inventory/search$', 'search'),
    url(r'^inventory$', 'inventory'),
)

# 库存产品出入库记录
urlpatterns += patterns('www.admin.views_inventory_record',

    url(r'^inventory_record/add_record$', 'add_record'),
    url(r'^inventory_record/search$', 'search'),
    url(r'^inventory_record$', 'inventory_record'),
)

# 库存产品对照
urlpatterns += patterns('www.admin.views_inventory_to_item',

    url(r'^inventory_to_item/drop_relationship$', 'drop_relationship'),
    url(r'^inventory_to_item/add_relationship$', 'add_relationship'),
    url(r'^inventory_to_item/get_relationship_by_id$', 'get_relationship_by_id'),
    url(r'^inventory_to_item/search$', 'search'),
    url(r'^inventory_to_item$', 'inventory_to_item'),
)

# 兼职人员管理
urlpatterns += patterns('www.admin.views_parttime_person',

    url(r'^parttime_person/get_persons_by_name$', 'get_persons_by_name'),
    url(r'^parttime_person/modify_person$', 'modify_person'),
    url(r'^parttime_person/add_person$', 'add_person'),
    url(r'^parttime_person/get_person_by_id$', 'get_person_by_id'),
    url(r'^parttime_person/search$', 'search'),
    url(r'^parttime_person$', 'parttime_person'),
)

# 兼职工作记录管理
urlpatterns += patterns('www.admin.views_parttime_record',

    url(r'^parttime_record/file_import$', 'file_import'),
    url(r'^parttime_record/remove_record$', 'remove_record'),
    url(r'^parttime_record/add_record$', 'add_record'),
    url(r'^parttime_record/get_record_by_id$', 'get_record_by_id'),
    url(r'^parttime_record/search$', 'search'),
    url(r'^parttime_record$', 'parttime_record'),
)

# 统计管理
urlpatterns += patterns('www.admin.views_statistics',
    url(r'^statistics_commission$', 'statistics_commission'),
    url(r'^statistics_commission/get_statistics_commission_data$', 'get_statistics_commission_data'),
    
    url(r'^statistics_orders$', 'statistics_orders'),
    url(r'^statistics_orders/get_statistics_orders_data$', 'get_statistics_orders_data'),

    url(r'^statistics_summary$', 'statistics_summary'),
    url(r'^statistics_summary/get_statistics_summary_data$', 'get_statistics_summary_data'),

    url(r'^statistics_sale_top$', 'statistics_sale_top'),
    url(r'^statistics_sale_top/get_statistics_sale_top_data$', 'get_statistics_sale_top_data'),

    url(r'^statistics_order_cost$', 'statistics_order_cost'),
    url(r'^statistics_order_cost/get_statistics_order_cost_data$', 'get_statistics_order_cost_data'),
    
    url(r'^statistics_chart$', 'statistics_chart'),
    url(r'^statistics_chart/get_chart_data$', 'get_chart_data'),
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