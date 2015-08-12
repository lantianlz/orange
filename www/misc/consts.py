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

    {'code': 'company_manage', 'name': u'公司管理', 'parent': None},
    {'code': 'add_company', 'name': u'添加公司', 'parent': 'company_manage'},
    {'code': 'query_company', 'name': u'查询公司', 'parent': 'company_manage'},
    {'code': 'modify_company', 'name': u'修改公司', 'parent': 'company_manage'},

    {'code': 'company_manager_manage', 'name': u'公司管理员管理', 'parent': None},
    {'code': 'add_company_manager', 'name': u'添加公司管理员', 'parent': 'company_manager_manage'},
    {'code': 'query_company_manager', 'name': u'查询公司管理员', 'parent': 'company_manager_manage'},
    {'code': 'modify_company_manager', 'name': u'修改公司管理员', 'parent': 'company_manager_manage'},
    {'code': 'remove_company_manager', 'name': u'删除公司管理员', 'parent': 'company_manager_manage'},

    {'code': 'item_manage', 'name': u'产品管理', 'parent': None},
    {'code': 'add_item', 'name': u'添加产品', 'parent': 'item_manage'},
    {'code': 'query_item', 'name': u'查询产品', 'parent': 'item_manage'},
    {'code': 'modify_item', 'name': u'修改产品', 'parent': 'item_manage'},

    {'code': 'meal_manage', 'name': u'套餐管理', 'parent': None},
    {'code': 'add_meal', 'name': u'添加套餐', 'parent': 'meal_manage'},
    {'code': 'query_meal', 'name': u'查询套餐', 'parent': 'meal_manage'},
    {'code': 'modify_meal', 'name': u'修改套餐', 'parent': 'meal_manage'},

    {'code': 'order_manage', 'name': u'订单管理', 'parent': None},
    {'code': 'add_order', 'name': u'添加订单', 'parent': 'order_manage'},
    {'code': 'query_order', 'name': u'查询订单', 'parent': 'order_manage'},
    {'code': 'modify_order', 'name': u'修改订单', 'parent': 'order_manage'},

    {'code': 'booking_manage', 'name': u'预订管理', 'parent': None},
    # {'code': 'add_booking', 'name': u'添加预订', 'parent': 'booking_manage'},
    {'code': 'query_booking', 'name': u'查询预订', 'parent': 'booking_manage'},
    {'code': 'modify_booking', 'name': u'修改预订', 'parent': 'booking_manage'},

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
