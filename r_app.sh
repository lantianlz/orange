#!/bin/bash
if [ x$1 == x ]; then
   echo 'which app?'
   exit 1;
fi
ports=`ps aux | grep $1: | grep -v grep | gawk '{print $NF}' | sed 's/:.../:/'`
for port in ${ports[*]}
do
    /opt/python2.7.2/bin/supervisorctl restart $port
done
supervisorctl restart www_worker:
