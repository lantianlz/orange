# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from common import utils, page
from misc.decorators import staff_required, common_ajax_response, verify_permission, member_required

from www.company.interface import MealBase, CompanyBase, ItemBase

@verify_permission('')
def meal(request, template_name='pc/admin/meal.html'):
    from www.company.models import Meal
    states = [{'name': x[1], 'value': x[0]} for x in Meal.state_choices]
    all_states = [{'name': x[1], 'value': x[0]} for x in Meal.state_choices]
    all_states.insert(0, {'name': u'全部', 'value': -1})
    
    init_add_item_ids = json.dumps([x.id for x in ItemBase().get_init_add_items()])

    today = datetime.datetime.now()
    start_date = today.strftime('%Y-%m-%d')
    end_date = (today + datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def format_meal(objs, num, show_items=False):
    data = []

    for x in objs:
        num += 1

        company = CompanyBase().get_company_by_id(x.company_id)
        items = []
        # 显示子项
        if show_items:
            for i in MealBase().get_items_of_meal(x.id):
                items.append({
                    'item_id': i.item.id,
                    'name': i.item.name,
                    'price': str(i.item.price),
                    'sale_price': str(i.item.sale_price),
                    'item_type': i.item.item_type,
                    'spec': i.item.spec,
                    'spec_text': i.item.get_spec_display(),
                    'code': i.item.code,
                    'img': i.item.img,
                    'amount': i.amount
                })

        data.append({
            'num': num,
            'meal_id': x.id,
            'company_id': company.id if company else '',
            'company_name': u'%s [%s人]' % (company.name, company.person_count) if company else '',
            'name': x.name,
            'des': x.des,
            'price': str(x.price),
            'start_date': str(x.start_date),
            'end_date': str(x.end_date),
            'state': x.state,
            'items': items
        })

    return data


@verify_permission('query_meal')
def search(request):
    data = []

    name = request.REQUEST.get('name')
    state = request.REQUEST.get('state')
    state = None if state == "-1" else state
    page_index = int(request.REQUEST.get('page_index'))

    objs = MealBase().search_meals_for_admin(state, name)

    page_objs = page.Cpt(objs, count=10, page=page_index).info

    # 格式化json
    num = 10 * (page_index - 1)
    data = format_meal(page_objs[0], num)

    return HttpResponse(
        json.dumps({'data': data, 'page_count': page_objs[4], 'total_count': page_objs[5]}),
        mimetype='application/json'
    )


@verify_permission('query_meal')
def get_meal_by_id(request):
    meal_id = request.REQUEST.get('meal_id')

    data = format_meal([MealBase().get_meal_by_id(meal_id)], 1, True)[0]

    return HttpResponse(json.dumps(data), mimetype='application/json')


def _get_items(item_ids, item_amounts):

    meal_items = []
    for x in range(len(item_ids)):
        meal_items.append({
            'item_id': item_ids[x],
            'amount': item_amounts[x]
        })

    return meal_items

@verify_permission('modify_meal')
@common_ajax_response
def modify_meal(request):

    meal_id = request.POST.get('meal_id')
    company = request.POST.get('company')
    name = request.POST.get('name')
    price = request.POST.get('price')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    des = request.POST.get('des')
    state = request.POST.get('state')

    # 套餐项目
    item_ids = request.POST.getlist('item-ids')
    item_amounts = request.POST.getlist('item-amounts')

    return MealBase().modify_meal(
        meal_id, company, name, price, start_date, 
        end_date, state, des, _get_items(item_ids, item_amounts)
    )

@verify_permission('add_meal')
@common_ajax_response
def add_meal(request):
    company = request.POST.get('company')
    name = request.POST.get('name')
    price = request.POST.get('price')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    des = request.POST.get('des')

    # 套餐项目
    item_ids = request.POST.getlist('item-ids')
    item_amounts = request.POST.getlist('item-amounts')

    flag, msg = MealBase().add_meal(
        company, name, price, start_date, end_date, des, 
        _get_items(item_ids, item_amounts)
    )
    return flag, msg.id if flag == 0 else msg


@member_required
def get_meals_by_name(request):
    '''
    根据名字查询套餐
    '''
    meal_name = request.REQUEST.get('meal_name')

    result = []

    meals = MealBase().get_meals_by_name(meal_name)

    if meals:
        for x in meals:
            result.append([x.id, u'%s [¥%s]' % (x.name, x.price), None, u'%s [¥%s]' % (x.name, x.price)])

    return HttpResponse(json.dumps(result), mimetype='application/json')