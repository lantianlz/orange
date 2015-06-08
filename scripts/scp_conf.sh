
#scp root@www.zhixuan.com:/etc/redis.conf /etc/

scp root@www.aoaoxc.com:/etc/nginx/nginx.conf /etc/nginx/
scp root@www.aoaoxc.com:/etc/nginx/conf.d/* /etc/nginx/conf.d/

scp -r root@www.aoaoxc.com:/etc/supervisord* /etc/
scp root@www.aoaoxc.com:/etc/init.d/supervisord /etc/init.d/