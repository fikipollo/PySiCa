#!/bin/ash

# First create the required directories
mkdir -p /var/log/pysica
mkdir -p /var/www/pysica/conf
touch /var/log/pysica/cache.log

if [[ ! -f /var/www/pysica/conf/server.cfg ]]; then
    cp /var/www/pysica/default/logging.default.cfg /var/www/pysica/conf/logging.cfg
    cp /var/www/pysica/default/server.default.cfg /var/www/pysica/conf/server.cfg
fi

# Read environment variables
SERVER_MODE="${SERVER_MODE:-web_server}"
SERVER_SOCKET_FILE="${SERVER_SOCKET_FILE:-}"
SERVER_BUFFER_SIZE=${SERVER_BUFFER_SIZE:-4096}
SERVER_HOST_NAME="${SERVER_HOST_NAME:-0.0.0.0}"

# Change the default configuration based on environment
sed -i 's/"SERVER_MODE".*/"SERVER_MODE" : "'${SERVER_MODE}'",/' /var/www/pysica/conf/server.cfg
sed -i 's#"SERVER_SOCKET_FILE".*#"SERVER_SOCKET_FILE" : "'${SERVER_SOCKET_FILE}'",#' /var/www/pysica/conf/server.cfg
sed -i 's/"SERVER_BUFFER_SIZE".*/"SERVER_BUFFER_SIZE" : '${SERVER_BUFFER_SIZE}',/' /var/www/pysica/conf/server.cfg
sed -i 's/"SERVER_HOST_NAME".*/"SERVER_HOST_NAME" : "'${SERVER_HOST_NAME}'",/' /var/www/pysica/conf/server.cfg

echo "#---------------------------------------------------------------------------------------------------"
echo "# Welcome to PySiCa (Python Simple Cache)"

# Launch server based on the current configuration
if [[ "$SERVER_MODE" == "socket_based" ]]; then
    echo "# Cache server is running in SOCKET mode"
    echo "# To change the running mode, please set the value for the variable SERVER_MODE in the"
    echo "# the server.cfg file. Available options are 'web_based' for RESTFUL mode based on HTTP "
    echo "# and 'socket_based' to use pure socket communication."
    echo "#---------------------------------------------------------------------------------------------------"
    python /var/www/pysica/server_sockets.py &
else
    echo "# Cache server is running as web server"
    echo "# To change the running mode, please set the value for the variable SERVER_MODE in the"
    echo "# the server.cfg file. Available options are 'web_based' for RESTFUL mode based on HTTP "
    echo "# and 'socket_based' to use pure socket communication."
    echo "#---------------------------------------------------------------------------------------------------"

    if [[ -f /tmp/pysica.pid ]]; then
      kill -9 `cat /tmp/pysica.pid`
      rm /tmp/pysica.*
    fi
    uwsgi --ini /var/pysica_uwsgi.ini
fi

echo "Listening to /var/log/pysica/cache.log"
tail -f /var/log/pysica/cache.log
