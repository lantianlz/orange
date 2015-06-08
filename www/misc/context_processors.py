# -*- coding: utf-8 -*-

"""
@attention: 定义全局上下文变量
@author: lizheng
@date: 2014-11-29
"""


def config(request):
    """
    @attention: Adds settings-related context variables to the context.
    """
    import datetime
    from django.conf import settings
    from common import cache

    return {
        'DEBUG': settings.DEBUG,
        'LOCAL_FLAG': settings.LOCAL_FLAG,
        'MEDIA_VERSION': cache.Cache(cache.CACHE_STATIC).get('media_version') or '000',  # 从缓存中取版本号
        'SERVER_DOMAIN': settings.SERVER_DOMAIN,
        'MAIN_DOMAIN': settings.MAIN_DOMAIN,
        'IMG0_DOMAIN': settings.IMG0_DOMAIN,
        "YEAR": datetime.datetime.now().strftime("%Y"),
    }
