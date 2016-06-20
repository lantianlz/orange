# -*- coding: utf-8 -*-

import json, datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission, log_sensitive_operation
from www.misc import qiniu_client
from common import utils, page

from www.company.models import Item
from www.company.interface import ItemBase

@verify_permission('')
def fruit_price(request, template_name='pc/admin/fruit_price.html'):
    items = ItemBase().get_items_by_type(1, [1]).order_by('-update_time')

    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('modify_fruit_price')
@common_ajax_response
@log_sensitive_operation
def modify_fruit_price(request):
    item_id = request.REQUEST.get('item_id')
    price = request.REQUEST.get('price')
    net_weight_rate = request.REQUEST.get('net_weight_rate')
    flesh_rate = request.REQUEST.get('flesh_rate')
    gross_profit_rate = request.REQUEST.get('gross_profit_rate')
    wash_floating_rate = request.REQUEST.get('wash_floating_rate')

    return ItemBase().modify_fruit_price(item_id, price, net_weight_rate, 
        flesh_rate, gross_profit_rate, wash_floating_rate)