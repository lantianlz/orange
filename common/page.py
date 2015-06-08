# -*- coding: utf-8 -*-

"""
@attention: 分页方法封装
@author: lizheng
@date: 2011-11-28
"""

from django.core.paginator import Paginator, InvalidPage, EmptyPage


class Cpt(object):

    """
    @attention: 分页处理类
    @author：lizheng
    @date: 2010-12-13
    """

    def __init__(self, objs=[], count=10, page=1):
        """
        @attention: 构造方法
        @param objs: 需要分页的列表
        @param count: 每页的数量
        @param page: 要取得的页
        """
        self.objs = objs
        self.count = count
        self.page = page
        self.Contacts = None
        self.Pt()

    def Pt(self):
        """
        @attention: 分页方法
        """
        objs, count, page = self.objs, self.count, self.page
        Pt = Paginator(objs, count)
        try:
            Page = int(page)
        except Exception:
            Page = 1
        try:
            Contacts = Pt.page(Page)
        except (EmptyPage, InvalidPage):
            if Page <= 0:
                Contacts = Pt.page(1)
            else:
                # 空的直接返回空，不再取最后一页
                Contacts = Pt.page(Pt.num_pages)
                Contacts.object_list = []
        self.Contacts = Contacts
        Ct = self.Contacts
        CurrentPage = Ct.number
        # 当前页、上一页、下一页、总页数、每页数量
        self.info = [list(self.Contacts.object_list), CurrentPage, Ct.previous_page_number(), Ct.next_page_number(), Ct.paginator.num_pages, Ct.paginator.count]
