# -*- coding: utf-8 -*-

"""
Created by Eric Lo on 2010-05-20.
Copyright (c) 2010 __lxneng@gmail.com__. http://lxneng.com All rights reserved.
"""
import os
from django.utils.encoding import smart_unicode


class Pinyin():

    def __init__(self, splitter='', data_path='pinyin.dat'):
        self.dict = {}
        py_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.abspath(os.path.join('%s/%s' % (py_path, data_path)))   # 取文件绝对位置
        for line in open(data_path):
            k, v = line.strip().split('\t')
            self.dict[k] = v
        self.splitter = splitter

    def get_pinyin(self, chars=u"你好吗"):
        result = []
        chars = smart_unicode(chars)
        for char in chars:
            key = "%X" % ord(char)
            try:
                result.append(self.dict[key].split(" ")[0].strip()[:-1].lower())
            except:
                result.append(char)
        return self.splitter.join(result)

    def get_initials(self, chars=u'你'):
        try:
            chars = smart_unicode(chars)
            data = u''
            for char in chars:
                char = smart_unicode(char)
                # print char.__repr__()
                # print self.dict["%X" % ord(char)].__repr__()
                data += self.dict["%X" % ord(char)].split(" ")[0][0].lower()
            return data
        except:
            return chars


if __name__ == '__main__':
    p = Pinyin()
    # print p.get_pinyin('中国')
    print p.get_initials('中')
