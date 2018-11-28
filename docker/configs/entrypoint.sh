#!/bin/ash

if [[ -f /tmp/pysica.pid ]]; then
  kill -9 `cat /tmp/pysica.pid`
  rm /tmp/pysica.*
fi

mkdir -p /var/log/pysica
mkdir -p /var/www/pysica/conf
touch /var/log/pysica/cache.log

uwsgi --ini /var/pysica_uwsgi.ini

tail -f /var/log/pysica/cache.log
