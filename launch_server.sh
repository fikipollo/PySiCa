#!/usr/bin/env bash

SCRIPTS_LOCATION=$(cd `dirname $0` && pwd)/

cd ${SCRIPTS_LOCATION}

if [[ ! -f conf/server.cfg ]]; then
    cp default/logging.default.cfg conf/logging.cfg
    cp default/server.default.cfg conf/server.cfg
fi

SERVER=$(awk -F":" 'BEGIN{server=""; port="";}{gsub("\"| |,",""); if($1 == "SERVER_HOST_NAME"){server=$2} else if($1 == "SERVER_PORT_NUMBER"){port=$2};}END{print server":"port}' conf/server.cfg )

uwsgi --http-socket ${SERVER} --wsgi-file server.py --callable application --processes=1 --enable-threads 
