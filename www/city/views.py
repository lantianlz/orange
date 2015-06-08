# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response

from www.city.interface import CityBase

cb = CityBase()


def open_citys_list(request, template_name='mobile/city/open_citys_list.html'):
    citys = cb.get_all_show_citys()
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def provinces_list(request, template_name='mobile/city/provinces_list.html'):
    provinces = cb.get_all_provinces()
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def citys_list(request, province_id, template_name='mobile/city/citys_list.html'):
    province = cb.get_province_by_id(province_id)
    if not province:
        raise Http404
    citys = cb.get_citys_by_province(province_id=province_id, is_show=False)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def unopen_city(request, city_id, template_name='mobile/city/unopen_city.html'):
    city = cb.get_city_by_id(city_id)
    if not city:
        raise Http404

    user_agent = request.META.get("HTTP_USER_AGENT", "").lower()
    if not("baidu" in user_agent or "spider" in user_agent):
        cb.add_vote_count(city)
    return render_to_response(template_name, locals(), context_instance=RequestContext(request))


def select_city(request, city_id):
    from www.account.interface import UserBase

    city = cb.get_city_by_id(city_id)
    if not city:
        raise Http404

    if request.user.is_authenticated():
        UserBase().change_user_city(request.user.id, city_id)
    request.session["city_id"] = city_id
    return HttpResponseRedirect("/car_wash/")
