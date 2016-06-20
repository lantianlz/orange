    # -*- coding: utf-8 -*-

'''
全局常量维护
'''

G_DICT_ERROR = {
    99600: u'不存在的用户',
    99700: u'权限不足',
    99800: u'参数缺失',
    99801: u'参数异常',
    99900: u'系统错误',
    0: u'成功'
}


PERMISSIONS = [
    {'code': 'user_manage', 'name': u'用户管理', 'parent': None},
    {'code': 'add_user', 'name': u'添加用户', 'parent': 'user_manage'},
    {'code': 'query_user', 'name': u'查询用户', 'parent': 'user_manage'},
    {'code': 'modify_user', 'name': u'修改用户', 'parent': 'user_manage'},
    {'code': 'remove_user', 'name': u'删除用户', 'parent': 'user_manage'},
    {'code': 'change_pwd', 'name': u'修改用户密码', 'parent': 'user_manage'},

    {'code': 'sale_man_manage', 'name': u'销售人员管理', 'parent': None},
    {'code': 'add_sale_man', 'name': u'添加销售人员', 'parent': 'sale_man_manage'},
    {'code': 'query_sale_man', 'name': u'查询销售人员', 'parent': 'sale_man_manage'},
    {'code': 'modify_sale_man', 'name': u'修改销售人员', 'parent': 'sale_man_manage'},

    {'code': 'company_manage', 'name': u'公司管理', 'parent': None},
    {'code': 'add_company', 'name': u'添加公司', 'parent': 'company_manage'},
    {'code': 'query_company', 'name': u'查询公司', 'parent': 'company_manage'},
    {'code': 'modify_company', 'name': u'修改公司', 'parent': 'company_manage'},

    {'code': 'company_manager_manage', 'name': u'公司管理员管理', 'parent': None},
    {'code': 'add_company_manager', 'name': u'添加公司管理员', 'parent': 'company_manager_manage'},
    {'code': 'query_company_manager', 'name': u'查询公司管理员', 'parent': 'company_manager_manage'},
    {'code': 'modify_company_manager', 'name': u'修改公司管理员', 'parent': 'company_manager_manage'},
    {'code': 'remove_company_manager', 'name': u'删除公司管理员', 'parent': 'company_manager_manage'},

    {'code': 'cash_account_manage', 'name': u'现金账户管理', 'parent': None},
    {'code': 'query_cash_account', 'name': u'查询现金账户', 'parent': 'cash_account_manage'},
    {'code': 'modify_cash_account', 'name': u'修改现金账户', 'parent': 'cash_account_manage'},

    {'code': 'cash_record_manage', 'name': u'现金流水管理', 'parent': None},
    {'code': 'add_cash_record', 'name': u'添加现金流水', 'parent': 'cash_record_manage'},
    {'code': 'query_cash_record', 'name': u'查询现金流水', 'parent': 'cash_record_manage'},
    {'code': 'modify_cash_record', 'name': u'修改现金流水', 'parent': 'cash_record_manage'},

    {'code': 'supplier_manage', 'name': u'供货商管理', 'parent': None},
    {'code': 'add_supplier', 'name': u'添加供货商', 'parent': 'supplier_manage'},
    {'code': 'query_supplier', 'name': u'查询供货商', 'parent': 'supplier_manage'},
    {'code': 'modify_supplier', 'name': u'修改供货商', 'parent': 'supplier_manage'},

    {'code': 'supplier_cash_account_manage', 'name': u'供货商现金账户管理', 'parent': None},
    {'code': 'query_supplier_cash_account', 'name': u'查询供货商现金账户', 'parent': 'supplier_cash_account_manage'},

    {'code': 'supplier_cash_record_manage', 'name': u'供货商现金流水管理', 'parent': None},
    {'code': 'add_supplier_cash_record', 'name': u'添加供货商现金流水', 'parent': 'supplier_cash_record_manage'},
    {'code': 'query_supplier_cash_record', 'name': u'查询供货商现金流水', 'parent': 'supplier_cash_record_manage'},

    {'code': 'item_manage', 'name': u'产品管理', 'parent': None},
    {'code': 'add_item', 'name': u'添加产品', 'parent': 'item_manage'},
    {'code': 'query_item', 'name': u'查询产品', 'parent': 'item_manage'},
    {'code': 'modify_item', 'name': u'修改产品', 'parent': 'item_manage'},

    {'code': 'meal_manage', 'name': u'套餐管理', 'parent': None},
    {'code': 'add_meal', 'name': u'添加套餐', 'parent': 'meal_manage'},
    {'code': 'query_meal', 'name': u'查询套餐', 'parent': 'meal_manage'},
    {'code': 'modify_meal', 'name': u'修改套餐', 'parent': 'meal_manage'},

    {'code': 'fruit_price_manage', 'name': u'水果价格管理', 'parent': None},
    {'code': 'modify_fruit_price', 'name': u'修改水果价格', 'parent': 'fruit_price_manage'},

    {'code': 'order_manage', 'name': u'订单管理', 'parent': None},
    {'code': 'add_order', 'name': u'添加订单', 'parent': 'order_manage'},
    {'code': 'query_order', 'name': u'查询订单', 'parent': 'order_manage'},
    {'code': 'modify_order', 'name': u'修改订单', 'parent': 'order_manage'},

    {'code': 'purchase_record_manage', 'name': u'采购流水管理', 'parent': None},
    {'code': 'add_purchase_record', 'name': u'添加采购流水', 'parent': 'purchase_record_manage'},
    {'code': 'query_purchase_record', 'name': u'查询采购流水', 'parent': 'purchase_record_manage'},
    {'code': 'modify_purchase_record', 'name': u'修改采购流水', 'parent': 'purchase_record_manage'},

    {'code': 'booking_manage', 'name': u'预订管理', 'parent': None},
    # {'code': 'add_booking', 'name': u'添加预订', 'parent': 'booking_manage'},
    {'code': 'query_booking', 'name': u'查询预订', 'parent': 'booking_manage'},
    {'code': 'modify_booking', 'name': u'修改预订', 'parent': 'booking_manage'},

    {'code': 'invoice_manage', 'name': u'发票管理', 'parent': None},
    {'code': 'add_invoice', 'name': u'添加发票', 'parent': 'invoice_manage'},
    {'code': 'query_invoice', 'name': u'查询发票', 'parent': 'invoice_manage'},
    {'code': 'modify_invoice', 'name': u'修改发票', 'parent': 'invoice_manage'},

    {'code': 'invoice_record_manage', 'name': u'发票记录管理', 'parent': None},
    {'code': 'add_invoice_record', 'name': u'添加发票记录', 'parent': 'invoice_record_manage'},
    {'code': 'query_invoice_record', 'name': u'查询发票记录', 'parent': 'invoice_record_manage'},
    {'code': 'modify_invoice_record', 'name': u'修改发票记录', 'parent': 'invoice_record_manage'},

    {'code': 'inventory_manage', 'name': u'库存产品管理', 'parent': None},
    {'code': 'add_inventory', 'name': u'添加库存产品', 'parent': 'inventory_manage'},
    {'code': 'query_inventory', 'name': u'查询库存产品', 'parent': 'inventory_manage'},
    {'code': 'modify_inventory', 'name': u'修改库存产品', 'parent': 'inventory_manage'},

    {'code': 'inventory_record_manage', 'name': u'库存产品记录管理', 'parent': None},
    {'code': 'add_inventory_record', 'name': u'添加库存产品记录', 'parent': 'inventory_record_manage'},
    {'code': 'query_inventory_record', 'name': u'查询库存产品记录', 'parent': 'inventory_record_manage'},
    {'code': 'modify_inventory_record', 'name': u'修改库存产品记录', 'parent': 'inventory_record_manage'},

    {'code': 'inventory_to_item_manage', 'name': u'库存产品对照管理', 'parent': None},
    {'code': 'add_inventory_to_item', 'name': u'添加库存产品对照', 'parent': 'inventory_to_item_manage'},
    {'code': 'query_inventory_to_item', 'name': u'查询库存产品对照', 'parent': 'inventory_to_item_manage'},
    {'code': 'modify_inventory_to_item', 'name': u'修改库存产品对照', 'parent': 'inventory_to_item_manage'},

    {'code': 'parttime_person_manage', 'name': u'兼职人员管理', 'parent': None},
    {'code': 'add_parttime_person', 'name': u'添加兼职人员', 'parent': 'parttime_person_manage'},
    {'code': 'query_parttime_person', 'name': u'查询兼职人员', 'parent': 'parttime_person_manage'},
    {'code': 'modify_parttime_person', 'name': u'修改兼职人员', 'parent': 'parttime_person_manage'},

    {'code': 'parttime_record_manage', 'name': u'兼职工作记录管理', 'parent': None},
    {'code': 'add_parttime_record', 'name': u'添加兼职工作记录', 'parent': 'parttime_record_manage'},
    {'code': 'query_parttime_record', 'name': u'查询兼职工作记录', 'parent': 'parttime_record_manage'},
    {'code': 'remove_parttime_record', 'name': u'删除兼职工作记录', 'parent': 'parttime_record_manage'},

    {'code': 'statistics_manage', 'name': u'统计管理', 'parent': None},
    {'code': 'statistics_sale_top', 'name': u'销售排行', 'parent': 'statistics_manage'},
    {'code': 'statistics_summary', 'name': u'综合统计', 'parent': 'statistics_manage'},
    {'code': 'statistics_orders', 'name': u'订单统计', 'parent': 'statistics_manage'},
    {'code': 'statistics_sale', 'name': u'销售额统计', 'parent': 'statistics_manage'},
    {'code': 'statistics_commission', 'name': u'邀请人返佣', 'parent': 'statistics_manage'},
    {'code': 'statistics_order_cost', 'name': u'成本统计', 'parent': 'statistics_manage'},

    {'code': 'city_manage', 'name': u'城市管理', 'parent': None},
    #{'code': 'add_city', 'name': u'添加城市', 'parent': 'city_manage'},
    {'code': 'query_city', 'name': u'查询城市', 'parent': 'city_manage'},
    {'code': 'modify_city', 'name': u'修改城市', 'parent': 'city_manage'},

    {'code': 'district_manage', 'name': u'区管理', 'parent': None},
    #{'code': 'add_district', 'name': u'添加区', 'parent': 'district_manage'},
    {'code': 'query_district', 'name': u'查询区', 'parent': 'district_manage'},
    {'code': 'modify_district', 'name': u'修改区', 'parent': 'district_manage'},

    {'code': 'tools', 'name': u'常用工具', 'parent': None},
    {'code': 'get_cache', 'name': u'查询缓存', 'parent': 'tools'},
    {'code': 'remove_cache', 'name': u'删除缓存', 'parent': 'tools'},
    {'code': 'modify_cache', 'name': u'修改缓存', 'parent': 'tools'},
    {'code': 'query_sensitive_operation_log', 'name': u'查询敏感操作日志', 'parent': 'tools'},
    
    {'code': 'permission_manage', 'name': u'权限管理', 'parent': None},
    {'code': 'add_user_permission', 'name': u'添加用户权限', 'parent': 'permission_manage'},
    {'code': 'query_user_permission', 'name': u'查询用户权限', 'parent': 'permission_manage'},
    {'code': 'modify_user_permission', 'name': u'修改用户权限', 'parent': 'permission_manage'},
    {'code': 'cancel_admin', 'name': u'取消管理员', 'parent': 'permission_manage'},
]
