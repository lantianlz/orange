# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from company.interface import OrderBase

@verify_permission('')
def month_gross_profit_analysis(request, template_name='pc/admin/month_gross_profit_analysis.html'):
    
    today = datetime.datetime.now()
    first_day = today.replace(day = 1)
    end_date = first_day - datetime.timedelta(days = 1)
    start_date = first_day.replace(year = today.year - 1)

    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('month_gross_profit_analysis')
def get_month_gross_profit_analysis_data(request):
    start_date = request.REQUEST.get('start_date')
    end_date = request.REQUEST.get('end_date')

    start_date, end_date = utils.get_date_range(start_date, end_date)

    all_cost_price = 0
    all_total_price = 0
    gross_profit_rate = 0
    data = []
    for x in OrderBase().get_month_gross_profit_analysis_data(start_date, end_date):
        data.append({
            'month': x[0], 
            'cost_price': round(x[1], 2), 
            'total_price': round(x[2], 2), 
            'gross_profit_rate': round(x[3]*100, 2)
        })
        all_cost_price += x[1]
        all_total_price += x[2]

    gross_profit_rate = round((1 - all_cost_price / all_total_price) * 100, 2) if all_total_price>0 else 0

    return HttpResponse(
        json.dumps({
            'data': data, 
            'all_cost_price': float(all_cost_price), 
            'all_total_price': float(all_total_price),
            'gross_profit_rate': float(gross_profit_rate)
        }),
        mimetype='application/json'
    ) 


@verify_permission('')
def company_gross_profit_analysis(request, template_name='pc/admin/company_gross_profit_analysis.html'):
    
    today = datetime.datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('company_gross_profit_analysis')
def get_company_gross_profit_analysis_data(request):
    start_date = request.REQUEST.get('start_date')
    end_date = request.REQUEST.get('end_date')
    name = request.REQUEST.get('name', '')
    rate = request.REQUEST.get('rate', 0)
    rate = int(rate)

    start_date, end_date = utils.get_date_range(start_date, end_date)

    all_cost_price = 0
    all_total_price = 0
    gross_profit_rate = 0
    data = []
    for x in OrderBase().get_company_gross_profit_analysis_data(start_date, end_date, name):
        temp_rate = round(x[4]*100, 2)
        if rate==0 or rate >= temp_rate:
            data.append({
                'name': x[0], 
                'short_name': x[1],
                'cost_price': round(x[2], 2), 
                'total_price': round(x[3], 2), 
                'gross_profit_rate': round(x[4]*100, 2)
            })
            all_cost_price += x[2]
            all_total_price += x[3]

    gross_profit_rate = round((1 - all_cost_price / all_total_price) * 100, 2) if all_total_price>0 else 0

    return HttpResponse(
        json.dumps({
            'data': data, 
            'all_cost_price': float(all_cost_price), 
            'all_total_price': float(all_total_price),
            'gross_profit_rate': float(gross_profit_rate)
        }),
        mimetype='application/json'
    ) 


@verify_permission('')
def order_gross_profit_analysis(request, template_name='pc/admin/order_gross_profit_analysis.html'):
    
    today = datetime.datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


@verify_permission('order_gross_profit_analysis')
def get_order_gross_profit_analysis_data(request):
    start_date = request.REQUEST.get('start_date')
    end_date = request.REQUEST.get('end_date')
    name = request.REQUEST.get('name', '')
    rate = request.REQUEST.get('rate', 0)

    start_date, end_date = utils.get_date_range(start_date, end_date)

    all_cost_price = 0
    all_total_price = 0
    gross_profit_rate = 0
    data = []
    for x in OrderBase().get_order_gross_profit_analysis_data(start_date, end_date, name, int(rate)):
        data.append({
            'name': x[0], 
            'short_name': x[1],
            'order_id': x[2],
            'order_no': x[3],
            'cost_price': round(x[4], 2), 
            'total_price': round(x[5], 2), 
            'gross_profit_rate': round(x[6]*100, 2)
        })
        all_cost_price += x[4]
        all_total_price += x[5]

    gross_profit_rate = round((1 - all_cost_price / all_total_price) * 100, 2) if all_total_price>0 else 0

    return HttpResponse(
        json.dumps({
            'data': data, 
            'all_cost_price': float(all_cost_price), 
            'all_total_price': float(all_total_price),
            'gross_profit_rate': float(gross_profit_rate)
        }),
        mimetype='application/json'
    ) 

    