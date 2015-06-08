# -*- coding: utf-8 -*-

import json
import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page, cache
from www.custom_tags.templatetags.custom_filters import str_display

from www.account.interface import UserBase, ExternalTokenBase


@verify_permission('')
def active_user(request, template_name='pc/admin/statistics_active_user.html'):
    from www.account.models import LastActive
    sources = [{'value': x[0], 'name': x[1]} for x in LastActive.last_active_source_choices]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('')
def retention(request, template_name='pc/admin/statistics_retention.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('statistics_active_user')
def get_active_user(request):
    page_index = int(request.REQUEST.get('page_index', 1))

    now = datetime.datetime.now()
    today = datetime.datetime(now.year, now.month, now.day)

    ub = UserBase()
    objs = ub.get_active_users(today)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化
    format_users = [ub.format_user_full_info(x.user_id) for x in page_objs[0]]

    data = []
    num = 10 * (page_index - 1) + 0

    for user in format_users:

        num += 1
        data.append({
            'num': num,
            'user_id': user.id,
            'user_avatar': user.get_avatar_65(),
            'user_nick': user.nick,
            'user_email': user.email,
            'source': user.last_active_source,
            'user_des': str_display(user.des, 17),
            'last_active': str(user.last_active),
            'state': user.state,
            'ip': user.last_active_ip
        })

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )

@verify_permission('')
def chart(request, template_name='pc/admin/statistics_chart.html'):
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('statistics_active_user')
def get_chart_data(request):
    from account.interface import UserBase
    from car_wash.interface import OrderBase

    #=================== 获取总注册用户数的数据
    register_x_data = []
    register_y_data = []
    data_length = 360
    register_count_data = dict(UserBase().get_count_group_by_create_time(data_length))
    
    for i in range(data_length):
        temp_date = datetime.datetime.now().date() - datetime.timedelta(data_length-i)
        temp_date = temp_date.strftime('%Y-%m-%d')
        register_x_data.append(temp_date)
        register_y_data.append(register_count_data.get(temp_date, 0))
    

    #=================== 获取今日注册用户数的数据
    today_register_x_data = []
    today_register_y_data = []
    today_register_data = dict(UserBase().get_toady_count_group_by_create_time())
    
    for i in range(24):
        temp_hour = '%02d' % i
        today_register_x_data.append(temp_hour)
        today_register_y_data.append(today_register_data.get(temp_hour, 0))


    #=================== 获取今日订单数的数据
    today_order_x_data = []
    today_order_y_data = []
    today_order_data = dict(OrderBase().get_toady_count_group_by_create_time())
    
    for i in range(24):
        temp_hour = '%02d' % i
        today_order_x_data.append(temp_hour)
        today_order_y_data.append(today_order_data.get(temp_hour, 0))


    #=================== 获取今日订单总额的数据
    today_balance_x_data = []
    today_balance_y_data = []
    today_balance_data = dict(OrderBase().get_toady_balance_group_by_create_time())
    
    for i in range(24):
        temp_hour = '%02d' % i
        today_balance_x_data.append(temp_hour)
        today_balance_y_data.append(float(today_balance_data.get(temp_hour, 0)))


    #=================== 获取缓存增量
    cache_obj = cache.Cache(cache.CACHE_STATIC)
    cache_str = cache_obj.get('statistics_chart') or '0,0,0,0'
    cache_str = cache_str.split(',')

    register_cache = int(cache_str[0].strip()) 
    today_register_cache = int(cache_str[1].strip()) 
    today_order_cache = int(cache_str[2].strip()) 
    today_balance_cache = float(cache_str[3].strip())

    return HttpResponse(
        json.dumps({
            'register_count': UserBase().get_all_users().count() + register_cache,
            'register_count_chart_data': [register_x_data, register_y_data],
            'today_register_count': sum(today_register_data.values()) + today_register_cache,
            'today_register_count_chart_data': [today_register_x_data, today_register_y_data],
            'today_order_count': sum(today_order_data.values()) + today_order_cache,
            'today_order_count_chart_data': [today_order_x_data, today_order_y_data],
            'today_balance': float(sum(today_balance_data.values())) + today_balance_cache,
            'today_balance_chart_data': [today_balance_x_data, today_balance_y_data]
        }),
        mimetype='application/json'
    ) 