"""
PySiCa, a simple Python Cache system

v0.2 December 2018
"""

import os
import falcon
import ujson
import logging.config
from logging.handlers import RotatingFileHandler
from shutil import copyfile
from pysica import PySiCa

class Application(object):

    def __init__(self):
        # ------------------------------------------------------------------------------------------
        # SERVER DEFINITION
        # ------------------------------------------------------------------------------------------
        self.settings = self.read_settings_file()

        # Enable the logging to file fir production
        logger = None
        if not self.settings.get("DEBUG", True):
            try:
                handler = RotatingFileHandler(self.settings.get("LOG_FILE"), maxBytes=31457280, backupCount=5)
                handler.setLevel(logging.INFO)
                handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s : %(funcName)s - %(message)s'))
                logger = logging.getLogger(__name__)
                logger.root.addHandler(handler)
            except Exception as e:
                raise Exception("Unable to open log file " + self.settings.get("LOG_FILE", "LOG FILE NOT SPECIFIED") + ". Error message: " + str(e))

        self.cache_instance = PySiCa(
            logger=logger,
            timeout=self.settings.get("TIMEOUT"),
            compress=self.settings.get("COMPRESS"),
            max_elems=self.settings.get("MAX_ELEMS"),
            clean_interval=self.settings.get("CLEAN_INTERVAL")
        )

    def on_get(self, req, resp, element_id=None):
        try:
            data_type = req.params.get('data_type')
            user_id   = req.params.get('user_id')
            reset_timeout = req.params.get('reset_timeout', False)
            timeout   = req.params.get('timeout')

            result = self.cache_instance.get_elem(element_id, data_type=data_type, user_id=user_id, reset_timeout=reset_timeout, timeout=timeout)
            resp.status = falcon.HTTP_200
            if len(result) > 0:
                resp.body = ujson.dumps({'success': True, 'result': result}, ensure_ascii=False)
            else:
                resp.body = ujson.dumps({'success': False}, ensure_ascii=False)
        except Exception as e:
            resp.status = falcon.HTTP_200
            resp.body = ujson.dumps({'success': False, 'message': "Failed while getting element. Error message: " + str(e)})

    def on_post(self, req, resp):
        try:
            element_id = req.media.get("element_id")
            data       = req.media.get("data")
            data_type  = req.media.get("data_type")
            user_id    = req.media.get("user_id")
            timeout    = req.media.get("timeout")  # in minutes
            compress   = req.media.get("compress")

            success = self.cache_instance.add(element_id, data, data_type, timeout=timeout, compress=compress, user_id=user_id)

            resp.status = falcon.HTTP_200
            resp.body = ujson.dumps({'success': success, 'element_id': element_id})
        except Exception as e:
            resp.status = falcon.HTTP_200
            resp.body = ujson.dumps({'success': False, 'message': "Failed while storing new element. Error message: " + str(e)})

    def on_delete(self, req, resp, element_id):
        try:
            user_id     = req.params.get("user_id", None)
            return_elem = req.params.get("return", False)

            result = self.cache_instance.remove(element_id, user_id=user_id)

            if return_elem:
                resp.body = ujson.dumps({'success': len(result) > 0, 'result': result}, ensure_ascii=False)
            else:
                resp.body = ujson.dumps({'success': len(result) > 0}, ensure_ascii=False)
        except Exception as e:
            resp.status = falcon.HTTP_200
            resp.body = ujson.dumps({'success': False, 'message': "Failed while removing element. Error message: " + str(e)})

    def on_put(self, req, resp, element_id):
        try:
            timeout = req.params.get("timeout", None)
            user_id = req.params.get("user_id", None)

            result = self.cache_instance.reset_timeout(element_id, timeout=timeout, user_id=user_id)

            if result:
                resp.body = ujson.dumps({'success': True}, ensure_ascii=False)
            else:
                resp.body = ujson.dumps({'success': False, 'message': "Element " + element_id + " is not in cache."}, ensure_ascii=False)
        except Exception as e:
            resp.status = falcon.HTTP_200
            resp.body = ujson.dumps({'success': False, 'message': "Failed while removing element. Error message: " + str(e)})

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
            settings["SERVER_HOST_NAME "] = SERVER_SETTINGS.get('SERVER_HOST_NAME', "0.0.0.0")
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


api = application = falcon.API()
application.req_options.auto_parse_form_urlencoded = True
application_functions = Application()
application.add_route('/api/get/{element_id}', application_functions)
application.add_route('/api/get', application_functions)
application.add_route('/api/remove/{element_id}', application_functions)
application.add_route('/api/reset/{element_id}', application_functions)
application.add_route('/api/add', application_functions)
