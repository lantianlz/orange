# -*- coding: utf-8 -*-

from common import debug
from www.misc import consts
from www.misc.decorators import cache_required

from www.city.models import City

dict_err = {
    50100: u'不存在的城市',
}
dict_err.update(consts.G_DICT_ERROR)


class CityBase(object):

    def __init__(self):
        pass

    def get_all_areas(self):
        return City.objects.filter(location_type=0)

    def get_all_provinces(self):
        return City.objects.filter(location_type=1)

    def get_all_citys(self):
        return City.objects.filter(location_type=2)

    def get_all_districts(self):
        return City.objects.filter(location_type=3)

    def get_all_show_citys(self):
        return City.objects.filter(location_type=2, is_show=True)

    def get_all_city_group_by_province(self):
        data = []
        areas = self.get_all_areas()
        provinces = City.objects.filter(location_type=1)
        citys = self.get_all_citys()

        for area in areas:
            area_provices = provinces.filter(area=area.id)
            data_citys = []
            for ap in area_provices:
                province_citys = citys.filter(province=ap.id)
                data_citys.append([ap, province_citys])
            data.append([area, data_citys])
        return data

    def get_citys_by_province(self, province_id, is_show=None):
        ps = dict(province=province_id)
        if is_show is not None:
            ps.update(dict(is_show=is_show))
        return self.get_all_citys().filter(**ps)

    def get_city_by_pinyin_abbr(self, pinyin_abbr):
        if pinyin_abbr:
            citys = self.get_all_citys().filter(pinyin_abbr=pinyin_abbr)
            if citys:
                return citys[0]

    def get_city_by_pinyin(self, pinyin):
        if pinyin:
            citys = self.get_all_citys().filter(pinyin=pinyin)
            if citys:
                return citys[0]

    def get_city_by_id(self, city_id):
        if city_id:
            citys = self.get_all_citys().filter(id=city_id)
            if citys:
                return citys[0]

    def get_citys_by_name(self, city_name):
        citys = []

        if city_name:
            citys = self.get_all_citys().filter(city__contains=city_name)

        return citys

    def get_city_by_name(self, city_name):
        objs = self.get_all_citys().filter(city=city_name)
        if objs:
            return objs[0]
        return None

    @cache_required(cache_key='province_by_id_%s', expire=3600 * 24)
    def get_province_by_id(self, province_id):
        objs = self.get_all_provinces().filter(id=province_id)
        if objs:
            return objs[0]

    def search_citys_for_admin(self, city_name, is_show=None, sort_by_province=True):

        citys = self.get_all_citys()

        if is_show is not None:
            citys = citys.filter(is_show=is_show)

        if city_name:
            citys = citys.filter(city__contains=city_name)

        if sort_by_province:
            citys = citys.order_by('-province')

        return citys

    def modify_city(self, city_id, **kwargs):

        if not city_id:
            return 99800, dict_err.get(99800)

        city = self.get_city_by_id(city_id)

        if not city:
            return 99800, dict_err.get(99800)

        if kwargs.get('pinyin'):
            temp = self.get_city_by_pinyin(kwargs.get('pinyin'))
            if temp and temp.id != city.id:
                return 50105, dict_err.get(50105)

        if kwargs.get('pinyin_abbr'):
            temp = self.get_city_by_pinyin_abbr(kwargs.get('pinyin_abbr'))
            if temp and temp.id != city.id:
                return 50106, dict_err.get(50106)

        try:
            for k, v in kwargs.items():
                setattr(city, k, v)

            city.save()

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    @cache_required(cache_key='city_district_%s', expire=3600 * 24)
    def get_district_by_id(self, district_id, must_update_cache=False):
        if district_id:
            districts = self.get_all_districts().filter(id=district_id)
            if districts:
                return districts[0]

    def get_districts_by_city(self, city_id, is_show=1):
        districts = []
        if city_id:
            ps = dict(city=city_id)
            if is_show is not None:
                ps.update(dict(is_show=is_show))
            districts = self.get_all_districts().filter(**ps)

        return districts

    def search_districts_for_admin(self, district_name, city_name, is_show=None):
        districts = self.get_all_districts()

        if is_show is not None:
            districts = districts.filter(is_show=is_show)

        if city_name:
            city = self.get_city_by_name(city_name)
            if city:
                districts = districts.filter(city=city.id)

        if district_name:
            districts = districts.filter(district__contains=district_name)

        return districts

    def modify_district(self, district_id, **kwargs):

        if not district_id:
            return 99800, dict_err.get(99800)

        district = self.get_district_by_id(district_id)

        if not district:
            return 99800, dict_err.get(99800)

        try:
            for k, v in kwargs.items():
                setattr(district, k, v)

            district.save()

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, dict_err.get(0)

    def add_vote_count(self, city, count=1):
        if not isinstance(city, City):
            city = self.get_city_by_id(city)
            if not city:
                return 50100, dict_err.get(50100)
        city.vote_count += 1
        city.save()
        return 0, dict_err.get(0)
