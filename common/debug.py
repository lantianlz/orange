# -*- coding: utf-8 -*-

"""
@attention: 调试信息获取、打印
@author: lizheng
@date: 2013-12-09
"""

import sys
import traceback
import datetime
import logging

from django.utils.encoding import smart_unicode
from django.conf import settings


class Frame(object):

    def __init__(self, tb):
        self.tb = tb
        frame = tb.tb_frame
        self.locals = {}
        self.locals.update(frame.f_locals)

    def print_path(self):
        return smart_unicode(traceback.format_tb(self.tb, limit=1)[0])

    def print_local(self):
        return u"\n".join(["%s=%s" % (k, self.dump_value(self.locals[k])) for k in self.locals])

    def dump_value(self, v):
        try:
            return smart_unicode(str(v))
        except:
            return u"value can not serilizable"


def get_debug_detail(e, log_it=True):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    frames = []
    tb = exc_traceback
    frames.append(tb.tb_frame)
    detail = u"system error -Exception:\n%s\n\ndetail info is:\n" % smart_unicode(e)
    while tb.tb_next:
        tb = tb.tb_next
        fm = Frame(tb)
        detail += unicode(fm.print_path())
        detail += u"\nlocals variables:\n"
        detail += unicode(fm.print_local())
        detail += u"\n" + u"-" * 100 + u"\n"
    if log_it:
        logging.error(detail)
    else:
        print str(e)
    return detail


def get_debug_detail_and_send_email(e):
    from www.tasks import async_send_email
    debug_detail = get_debug_detail(e)
    if isinstance(debug_detail, (list, tuple)):
        debug_detail = str(debug_detail)
    debug_detail = u"%s\n%s" % (str(datetime.datetime.now()), debug_detail)
    async_send_email(settings.NOTIFICATION_EMAIL, u"%s direct error" % (settings.SERVER_NAME, ),
                     debug_detail, type="text")
