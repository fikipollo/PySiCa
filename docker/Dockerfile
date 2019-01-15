############################################################
# Dockerfile to build iGenomix CGT viewer container images
# Based on official HTTPD
############################################################

# Set the base image to official Python
FROM python:3.5.6-alpine3.8

# File Author / Maintainer
MAINTAINER Rafael Hernandez <https://github.com/fikipollo>

################## BEGIN INSTALLATION ######################
#INSTALL THE DEPENDENCIES

RUN set -x \
    && apk --update --no-cache add make unzip \
    && apk --update --no-cache --virtual .build-dep add build-base linux-headers tzdata \
    && cp /usr/share/zoneinfo/Europe/Madrid /etc/localtime \
    && echo "Europe/Madrid" >  /etc/timezone \
    && pip install --upgrade pip \
    && pip install --no-cache-dir cython \
    && pip install --no-cache-dir ujson \
    && pip install --no-cache-dir --no-binary :all: falcon \
    && pip install --no-cache-dir APScheduler \
    && pip install --no-cache-dir https://github.com/unbit/uwsgi/archive/uwsgi-2.0.zip#egg=uwsgi \
    && apk del .build-dep \
    && mkdir -p /var/www/

COPY configs/* /tmp/

RUN unzip /tmp/pysica.zip -d /tmp/pysica \
    && mv /tmp/pysica_uwsgi.ini /var/ \
    && mv /tmp/pysica /var/www/pysica \
    && mv /tmp/entrypoint.sh /usr/bin/entrypoint.sh \
    && chmod +x /usr/bin/entrypoint.sh \
    && rm -r /tmp/*

##################### INSTALLATION END #####################

EXPOSE 4444

ENTRYPOINT ["/usr/bin/entrypoint.sh"]
