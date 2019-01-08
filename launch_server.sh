#!/usr/bin/env bash

SCRIPTS_LOCATION=$(cd `dirname $0` && pwd)/

cd ${SCRIPTS_LOCATION}

if [[ ! -f conf/server.cfg ]]; then
    cp default/logging.default.cfg conf/logging.cfg
    cp default/server.default.cfg conf/server.cfg
fi

# Check the server mode at server.cfg
cat conf/server.cfg | grep SERVER_MODE | grep "socket_based" > /dev/null
SERVER_MODE=$?

echo "#---------------------------------------------------------------------------------------------------"
echo "# Welcome to PySiCa (Python Simple Cache)"

if [[ "$SERVER_MODE" == "0" ]]; then
    echo "# Cache server is running in SOCKET mode"
    echo "# To change the running mode, please set the value for the variable SERVER_MODE in the"
    echo "# the server.cfg file. Available options are 'web_based' for RESTFUL mode based on HTTP "
    echo "# and 'socket_based' to use pure socket communication."
    echo "#---------------------------------------------------------------------------------------------------"
    python server_sockets.py
else
    echo "# Cache server is running as web server"
    echo "# To change the running mode, please set the value for the variable SERVER_MODE in the"
    echo "# the server.cfg file. Available options are 'web_based' for RESTFUL mode based on HTTP "
    echo "# and 'socket_based' to use pure socket communication."
    echo "#---------------------------------------------------------------------------------------------------"
    SERVER_NAME=$(awk -F":" 'BEGIN{server=""; port="";}{gsub("\"| |,",""); if($1 == "SERVER_HOST_NAME"){server=$2} else if($1 == "SERVER_PORT_NUMBER"){port=$2};}END{print server":"port}' conf/server.cfg )
    uwsgi --http-socket ${SERVER_NAME} --wsgi-file server_http.py --callable application --processes=1 --enable-threads
fi

