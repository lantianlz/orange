# -*- coding: utf-8 -*-

import json
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings

from www.misc.decorators import staff_required, common_ajax_response, verify_permission
from www.misc import qiniu_client
from common import utils, page

from www.car_wash.interface import CompanyBase, ServiceTypeBase

@verify_permission('')
def batch_price(request, template_name='pc/admin/company_batch_price.html'):
    service_types = [{'value': x.id, 'name': x.name} for x in ServiceTypeBase().get_all_types(True)]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('batch_save_price')
@common_ajax_response
def save_price(request):
	company_id = request.REQUEST.get('company_id')
	service_type_id = request.REQUEST.get('service_type_id')
	sale_price = request.REQUEST.get('sale_price')
	origin_price = request.REQUEST.get('origin_price')
	clear_price = request.REQUEST.get('clear_price')
	sort_num = request.REQUEST.get('sort')

	return CompanyBase().batch_save_price(company_id, service_type_id, sale_price, origin_price, clear_price, sort_num)