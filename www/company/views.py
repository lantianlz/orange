# -*- coding: utf-8 -*-

import json, time

from django.http import HttpResponse

from misc.decorators import common_ajax_response
from www.company.interface import BookingBase

@common_ajax_response
def booking(request):
    
    company_name = request.REQUEST.get('company')
    staff_name = request.REQUEST.get('name')
    mobile = request.REQUEST.get('mobile')
    source = request.REQUEST.get('source')

    return BookingBase().add_booking(company_name, staff_name, mobile, source)