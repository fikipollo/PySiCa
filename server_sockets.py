"""
PySiCa, a simple Python Cache system

v0.2 December 2018
"""

import os
import ujson
import socket
import logging.config
import zlib
from logging.handlers import RotatingFileHandler
from shutil import copyfile
from pysica import PySiCa
from struct import unpack, pack


class Application(object):
    # ------------------------------------------------------------------------------------------
    # SERVER DEFINITION
    # ------------------------------------------------------------------------------------------
    def __init__(self):
        self.settings = self.read_settings_file()
        self.buffer_size = 0
        self.socket = None
        # Enable the logging to file for production
        self.logger = self.configure_logging()
        # Create the instance for the cache
        self.cache_instance = PySiCa(
            logger=self.logger,
            timeout=self.settings.get("TIMEOUT"),
            compress=self.settings.get("COMPRESS"),
            max_elems=self.settings.get("MAX_ELEMS"),
            clean_interval=self.settings.get("CLEAN_INTERVAL")
        )

    def run_server(self):
        self.buffer_size = self.settings.get("SERVER_BUFFER_SIZE")
        self.logger.info("Buffer size is " + self.humanize_bytes(int(self.buffer_size)))
        socket_file = self.settings.get("SERVER_SOCKET_FILE")
        if socket_file != "" and socket_file is not None:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:
                os.remove(socket_file)
            except OSError:
                pass
            self.socket.bind(socket_file)
            os.chmod(socket_file, 0o777)
            self.logger.info("Listening on " + socket_file + "...")
        else:
            # Use network socket by default
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = self.settings.get("SERVER_HOST_NAME")
            port = self.settings.get("SERVER_PORT_NUMBER")
            self.socket.bind((host, port))
            self.logger.info("Listening on %s:%s..." % (host, str(port)))
        # Listen to the socket
        self.socket.listen(1)

    def handle_requests(self):
        try:
            while True:
                # First read the entire request
                (request, connection) = self.read_request()
                # Now, check the target function to use
                target = request.get("target")
                respond = None
                if target == "add":
                    respond = self.on_post(request)
                elif target == "get":
                    respond = self.on_get(request)
                elif target == "remove":
                    respond = self.on_delete(request)
                elif target == "reset":
                    respond = self.on_reset(request)
                else:
                    respond = {'success': False, 'message': target + " is not a valid option."}
                # Return the respond
                self.send_respond(connection, respond)
        except Exception as ex:
            self.logger.error("Failed while reading request data. Error message: " + str(ex))
        finally:
            self.close()

    def on_post(self, request):
        try:
            success = self.cache_instance.add(request.get("element_id"), request.get("data"), request.get("data_type"), timeout=request.get("timeout"), compress=request.get("compress"), user_id=request.get("user_id"))
            return {'success': success, 'element_id': request.get("element_id")}
        except Exception as e:
            return {'success': False, 'message': "Failed while storing new element. Error message: " + str(e)}

    def on_get(self, request):
        try:
            result = self.cache_instance.get_elem(request.get("element_id"), data_type=request.get("data_type"), user_id=request.get("user_id"), reset_timeout=request.get("reset_timeout"), timeout=request.get("timeout"))
            if len(result) > 0:
                return {'success': True, 'result': result}
            else:
                return {'success': False}
        except Exception as e:
            return {'success': False, 'message': "Failed while getting element. Error message: " + str(e)}

    def on_delete(self, request):
        try:
            result = self.cache_instance.remove(request.get("element_id"), user_id=request.get("user_id"))
            return {'success': len(result) > 0}
        except Exception as e:
            return {'success': False, 'message': "Failed while removing element. Error message: " + str(e)}

    def on_reset(self, request):
        try:
            result = self.cache_instance.reset_timeout(request.get("element_id"), timeout=request.get("timeout"), user_id=request.get("user_id"))
            return {'success': result}
        except Exception as e:
            return {'success': False, 'message': "Element " + request.get("element_id") + " is not in cache."}

    def send_respond(self, connection, data):
        try:
            data = zlib.compress(ujson.dumps(data).encode("utf-8"))
            # use struct to make sure we have a consistent endianness on the length
            length = pack('>Q', len(data))
            # sendall to make sure it blocks if there's back-pressure on the socket
            connection.sendall(length)
            connection.sendall(data)
        finally:
            connection.shutdown(socket.SHUT_WR)
            connection.close()

    def read_request(self):
        (connection, addr) = self.socket.accept()
        bs = connection.recv(8)
        (data_length,) = unpack('>Q', bs)
        data = b''
        while len(data) < data_length:
            # doing it in batches is generally better than trying
            # to do it all in one go, so I believe.
            to_read = data_length - len(data)
            data += connection.recv(self.buffer_size if to_read > self.buffer_size else to_read)
        return ujson.loads(zlib.decompress(data)), connection

    def close(self):
        self.socket.close()
        self.socket = None

    def read_settings_file(self):
        conf_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf/server.cfg")
        logging_conf_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf/logging.cfg")
        # Copy the default settings
        if not os.path.isfile(conf_path):
            copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "default/server.default.cfg"), conf_path)
            copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "default/logging.default.cfg"), logging_conf_path)

        settings = {}
        if os.path.isfile(conf_path):
            config = ujson.load(open(conf_path))

            SERVER_SETTINGS = config.get("SERVER_SETTINGS", {})
            settings["SERVER_SOCKET_FILE"] = SERVER_SETTINGS.get('SERVER_SOCKET_FILE', '')
            settings["SERVER_BUFFER_SIZE"] = int(SERVER_SETTINGS.get('SERVER_BUFFER_SIZE', 4096))
            settings["SERVER_HOST_NAME"] = SERVER_SETTINGS.get('SERVER_HOST_NAME', "0.0.0.0")
            settings["SERVER_SUBDOMAIN"] = SERVER_SETTINGS.get('SERVER_SUBDOMAIN', "")
            settings["SERVER_PORT_NUMBER"] = SERVER_SETTINGS.get('SERVER_PORT_NUMBER', 8081)
            settings["DEBUG"] = SERVER_SETTINGS.get('DEBUG', False)
            settings["TMP_DIRECTORY"] = SERVER_SETTINGS.get('TMP_DIRECTORY', "/tmp")
            settings["LOG_FILE"] = SERVER_SETTINGS.get('LOG_FILE', "/tmp/queue.log")

            CACHE_SETTINGS = config.get("CACHE_SETTINGS", {})
            settings["TIMEOUT"] = CACHE_SETTINGS.get('TIMEOUT', 10)
            settings["COMPRESS"] = CACHE_SETTINGS.get('COMPRESS', True)
            settings["MAX_ELEMS"] = CACHE_SETTINGS.get('MAX_ELEMS', 50)
            settings["CLEAN_INTERVAL"] = CACHE_SETTINGS.get('CLEAN_INTERVAL', 30)

        # PREPARE LOGGING
        logging.config.fileConfig(logging_conf_path)

        return settings

    def configure_logging(self):
        if not self.settings.get("DEBUG", True):
            try:
                logger = logging.getLogger()
                logger.handlers=[]
                #
                handler = RotatingFileHandler(self.settings.get("LOG_FILE"), maxBytes=31457280, backupCount=5)
                handler.propagate = False
                handler.setLevel(logging.INFO)
                handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s : %(funcName)s - %(message)s'))
                logger.root.addHandler(handler)
                return logger
            except Exception as e:
                raise Exception("Unable to open log file " + self.settings.get("LOG_FILE", "LOG FILE NOT SPECIFIED") + ". Error message: " + str(e))
        else:
            return logging.root

    def humanize_bytes(self, size):
        for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(size) < 1024.0:
                return "%3.1f %s%s" % (size, unit, 'B')
            size /= 1024.0
        return "%.1f%s%s" % (size, 'Yi', 'B')


if __name__ == '__main__':
    app = Application()
    app.run_server()
    app.handle_requests()
