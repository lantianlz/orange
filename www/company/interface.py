# -*- coding: utf-8 -*-

import datetime
import logging
import time
from django.db import transaction
from django.utils.encoding import smart_unicode
from django.conf import settings

from common import utils, debug, validators, cache, raw_sql
from www.misc.decorators import cache_required
from www.misc import consts

from models import Item

dict_err = {
    20101: u'茶点产品名重复'
}
dict_err.update(consts.G_DICT_ERROR)

class ItemBase(object):

    def add_item(self, name, item_type, spec, price, sort):

        if None in (name, item_type, price):
            return 99800, dict_err.get(99800)

        if Item.objects.filter(name=name):
            return 20101, dict_err.get(20101)
        
        try:
            item = Item.objects.create(
                name = name,
                item_type = item_type,
                spec = spec,
                price = price,
                sort = sort
            )

        except Exception, e:
            debug.get_debug_detail(e)
            return 99900, dict_err.get(99900)

        return 0, item

    def search_items_for_admin(self, name):
        objs = Item.objects.all()

        if name:
            objs = objs.filter(name__contains=name)

        return objs