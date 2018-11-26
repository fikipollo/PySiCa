############################################################
# Dockerfile to build iGenomix CGT viewer container images
# Based on official HTTPD
############################################################

# Set the base image to official HTTP
FROM ubuntu:16.04

# File Author / Maintainer
MAINTAINER Rafael Hernandez <https://github.com/fikipollo>

################## BEGIN INSTALLATION ######################
#INSTALL THE DEPENDENCIES

RUN apt-get update  \
    && apt-get install --no-install-recommends -y uwsgi unzip python-dev build-essential uwsgi-plugin-python \
    && apt-get clean

COPY configs/* /tmp/

RUN unzip /tmp/pysica.zip -d /tmp/pysica \
    && mv /tmp/pysica_uwsgi.ini /var/ \
    && mkdir -p /var/www/ \
    && mv /tmp/pysica /var/www/pysica \
    && mv /tmp/entrypoint.sh /usr/bin/entrypoint.sh \
    && chmod +x /usr/bin/entrypoint.sh

RUN python /tmp/get-pip.py \
    && pip install -U pip \
    && pip install -vU pathlib \
    && pip install --upgrade incremental \
    && pip install -r /var/www/pysica/requirements.txt \
    && rm -r /tmp/*

##################### INSTALLATION END #####################

EXPOSE 4444

ENTRYPOINT ["/usr/bin/entrypoint.sh"]
