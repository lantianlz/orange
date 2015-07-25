# -*- coding: utf-8 -*-

import os
import sys
import tornado.ioloop
import tornado.web
import tornado.wsgi
import tornado.httpserver
from django.core.handlers.wsgi import WSGIHandler

# 设置 Django 设置模块
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(_HERE)
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"


def main(port):
    wsgi_app = tornado.wsgi.WSGIContainer(WSGIHandler())

    tornado_app = tornado.web.Application(
        [('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
         ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    try:
        import setproctitle
        setproctitle.setproctitle('www:' + sys.argv[1])
    except ImportError:
        pass
    main(int(sys.argv[1]))
