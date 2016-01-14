# -*- coding: utf-8 -*-

import json
import random
import datetime
import decimal
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page, cache
from www.custom_tags.templatetags.custom_filters import str_display

from www.account.interface import UserBase, ExternalTokenBase
from www.company.interface import StatisticsBase, SaleManBase

@verify_permission('')
def statistics_order_cost(request, template_name='pc/admin/statistics_order_cost.html'):
    
    today = datetime.datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('')
def statistics_chart(request, template_name='pc/admin/statistics_chart.html'):
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('')
def statistics_sale_top(request, template_name='pc/admin/statistics_sale_top.html'):
    today = datetime.datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('')
def statistics_summary(request, template_name='pc/admin/statistics_summary.html'):
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('')
def statistics_orders(request, template_name='pc/admin/statistics_orders.html'):
    today = datetime.datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('')
def statistics_commission(request, template_name='pc/admin/statistics_commission.html'):
    today = datetime.datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('')
def get_chart_data(request):
    days = 100
    x_data = [(datetime.datetime.now() - datetime.timedelta(days=(days-x))).strftime('%Y-%m-%d') for x in range(days)]

    data = {
        'order_count': 2765,
        'order_x_data': x_data,
        'order_y_data': [random.randint(0, 100) for x in range(days)],

        'amount_count': 28742.45,
        'amount_x_data': x_data,
        'amount_y_data': [random.randint(0, 1000) for x in range(days)],

        'fruit_count': 343,
        'fruit_x_data': x_data,
        'fruit_y_data': [random.randint(0, 400) for x in range(days)],

        'cake_count': 587,
        'cake_x_data': x_data,
        'cake_y_data': [random.randint(0, 300) for x in range(days)],

        'user_count': 1873,
        'user_x_data': x_data,
        'user_y_data': [random.randint(0, 200) for x in range(days)],
    }

    return HttpResponse(
        json.dumps(data),
        mimetype='application/json'
    )

@verify_permission('statistics_sale_top')
def get_statistics_sale_top_data(request):
    
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)

    # 获取所有销售人员列表
    sale_man_dict = {}
    for x in SaleManBase().get_all_sale_man(True):
        user = UserBase().get_user_by_id(x.user_id)
        sale_man_dict[x.user_id] = {
            'sale_by_id': x.user_id,
            'sale_by_nick': user.nick,
            'sale_by_avatar': user.get_avatar_65(),
            'total': 0,
            'meals': [],
            'companys': []
        }

    # 获取符合条件的销售数据
    data = {}
    objs = StatisticsBase().statistics_sale(start_date, end_date)
    for x in objs:
        key = x.company.sale_by
        if not data.has_key(key):
            
            user = UserBase().get_user_by_id(key)
            data[key] = {
                'sale_by_id': key,
                'sale_by_nick': user.nick,
                'sale_by_avatar': user.get_avatar_65(),
                'total': 0,
                'meals': [],
                'companys': []
            }

        data[key]['total'] += x.get_expect_price_per_month(start_date, end_date, x.company.sale_date)
        data[key]['meals'].append({
            'meal_name': x.name,
            'company_name': x.company.name,
            'sale_date': str(x.company.sale_date)[:10],
            'cycle': x.cycle,
            't_type': x.get_t_type_display(),
            'price': str(x.price),
            'expect_price': str(x.get_expect_price_per_month(start_date, end_date, x.company.sale_date))
        })
        data[key]['companys'].append(x.company.id)

    # 合并数据
    sale_man_dict.update(data)

    data = sale_man_dict.values()
    data.sort(key=lambda x: x['total'], reverse=True)
    # 获取最大的销售额，用于计算比率
    max_total = data[0]['total'] if data else 0

    all_company = 0
    all_total = 0
    for x in data:
        # 计算比率
        x['rate'] = round(x['total'] / max_total * 100, 1) if max_total != 0 else 0
        # 转json
        all_total += x['total']
        x['total'] = str(x['total']) if x['total'] > 0 else '0'
        # 计算总公司
        x['companys'] = len(set(x['companys']))
        all_company += x['companys']

    average_company = round(all_total / (all_company or 1 ), 1)
    average_company = str(average_company)
    all_total = str(all_total)

    return HttpResponse(
        json.dumps({'data': data, 'all_total': all_total, 'all_company': all_company, 'average_company': average_company}),
        mimetype='application/json'
    )


@verify_permission('statistics_summary')
def get_statistics_summary_data(request):

    statistics_summary_data = StatisticsBase().statistics_summary()

    return HttpResponse(
        json.dumps(statistics_summary_data),
        mimetype='application/json'
    )


@verify_permission('statistics_orders')
def get_statistics_orders_data(request):
    days = 100
    x_data = [(datetime.datetime.now() - datetime.timedelta(days=(days-x))).strftime('%Y-%m-%d') for x in range(days)]

    data = {
        'order_count_x_data': x_data,
        'order_count_y_data': [random.randint(0, 100) for x in range(days)],

        'person_count_x_data': x_data,
        'person_count_y_data': [random.randint(0, 100) for x in range(days)],

        'order_price_x_data': x_data,
        'order_price_y_data': [random.randint(0, 100) for x in range(days)],
    }

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)

    # =================== 获取日订单的数量
    order_count_x_data = []
    order_count_y_data = []
    order_count = 0
    order_per_count = 0
    for x in StatisticsBase().get_order_count_group_by_confirm_time(start_date, end_date):
        order_count_x_data.append(x[0])
        order_count_y_data.append(x[1])
        order_count += x[1]
    days = len(order_count_x_data) if order_count_x_data else 1
    order_per_count = (order_count / days) if (order_count % days) == 0 else (order_count / days + 1)

    # =================== 获取日服务人次的数量
    person_count_x_data = []
    person_count_y_data = []
    person_count = 0
    person_per_count = 0
    for x in StatisticsBase().get_person_count_group_by_confirm_time(start_date, end_date):
        person_count_x_data.append(x[0])
        person_count_y_data.append(str(x[1]))
        person_count += x[1]
    days = len(person_count_x_data) if person_count_x_data else 1
    person_per_count = '%.f' % (person_count / days)

    # =================== 获取日订单总金额
    order_price_x_data = []
    order_price_y_data = []
    order_price = 0
    order_per_price = 0
    order_per_day_price = 0
    for x in StatisticsBase().get_order_price_group_by_confirm_time(start_date, end_date):
        order_price_x_data.append(x[0])
        order_price_y_data.append(str(x[1]))
        order_price += x[1]
    days = len(order_price_x_data) if order_price_x_data else 1
    order_per_day_price = '%.2f' % (order_price / days)
    order_per_price = '%.2f' % (order_price / (order_count if order_count != 0 else 1) )

    # =================== 获取月订单总金额
    order_price_of_month_x_data = []
    order_price_of_month_y_data = []
    order_price_of_month_mark_point_data = []
    order_price_of_month = 0
    order_per_price_of_month = 0
    for x in StatisticsBase().get_order_price_group_by_confirm_time_of_month(start_date, end_date):
        v = '%.2f' % (x[1]/decimal.Decimal(1000.0))
        order_price_of_month_x_data.append(x[0])
        order_price_of_month_y_data.append(v)
        order_price_of_month += x[1]
        order_price_of_month_mark_point_data.append({
            'coord': [x[0], v], 
            'name': '订单总金额', 
            'value': str(x[1])
        })
        
    months = len(order_price_of_month_x_data) if order_price_of_month_x_data else 1
    order_per_price_of_month = '%.2f' % (order_price_of_month / months)

    data = {
        'order_count': str(order_count),
        'order_per_count': str(order_per_count),
        'order_count_x_data': order_count_x_data,
        'order_count_y_data': order_count_y_data,
        'person_count': str(person_count),
        'person_per_count': str(person_per_count),
        'person_count_x_data': person_count_x_data,
        'person_count_y_data': person_count_y_data,
        'order_price': str(order_price),
        'order_per_day_price': str(order_per_day_price),
        'order_per_price': str(order_per_price),
        'order_price_x_data': order_price_x_data,
        'order_price_y_data': order_price_y_data,
        'order_price_of_month_x_data': order_price_of_month_x_data,
        'order_price_of_month_y_data': order_price_of_month_y_data,
        'order_price_of_month': str(order_price_of_month),
        'order_per_price_of_month': order_per_price_of_month,
        'order_price_of_month_mark_point_data': order_price_of_month_mark_point_data
    }
    return HttpResponse(
        json.dumps(data),
        mimetype='application/json'
    )


@verify_permission('statistics_commission')
def get_statistics_commission_data(request):

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)

    data = {}

    for x in StatisticsBase().statistics_commission(start_date, end_date):
        key = x.company.invite_by
        user = UserBase().get_user_by_id(key)

        if not data.has_key(key):
            data[key] = {
                'user_id': key,
                'user_nick': user.nick,
                'user_avatar': user.get_avatar_65(),
                'total_price': 0,
                'meals': []
            }

        # 订单金额 199以上的奖励100  其他奖励50
        temp_price = 100 if x.price >= 199 else 50

        data[key]['total_price'] += temp_price
        data[key]['meals'].append({
            'company_name': x.company.name,
            'company_short_name': x.company.short_name,
            'meal_name': x.name,
            'meal_price': str(x.price),
            'date': str(x.company.sale_date)[:10],
            'user_nick': user.nick,
            'price': str(temp_price)
        })

    for x in data.values():
        x['total_price'] = str(x['total_price'])

    return HttpResponse(
        json.dumps(data.values()),
        mimetype='application/json'
    )


@verify_permission('statistics_order_cost')
def get_statistics_order_cost_data(request):

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_date, end_date = utils.get_date_range(start_date, end_date)
    
    statistics_order_cost_data = StatisticsBase().statistics_order_cost(start_date, end_date)

    return HttpResponse(
        json.dumps(statistics_order_cost_data),
        mimetype='application/json'
    )
