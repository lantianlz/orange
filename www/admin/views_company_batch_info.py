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
def batch_info(request, template_name='pc/admin/company_batch_info.html'):
    service_types = [{'value': x.id, 'name': x.name} for x in ServiceTypeBase().get_all_types(True)]
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))

@verify_permission('batch_save_info')
@common_ajax_response
def save_info(request):
	company_id = request.REQUEST.get('company_id')
	business_hours = request.REQUEST.get('business_hours')
	lowest_sale_price = request.REQUEST.get('lowest_sale_price')
	lowest_origin_price = request.REQUEST.get('lowest_origin_price')
	imgs = request.REQUEST.get('imgs')
	des = request.REQUEST.get('des')
	note = request.REQUEST.get('note')

	return CompanyBase().batch_save_info(company_id, business_hours,
		lowest_sale_price, lowest_origin_price, imgs, des, note)