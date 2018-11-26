"""
PySiCa, a simple Python Cache system

v0.1 December 2018
"""

import os
import json
import logging.config
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from flask_cors import CORS
from shutil import copyfile
from PySiCa import PySiCa


class Application(object):

    def __init__(self):
        # ------------------------------------------------------------------------------------------
        # SERVER DEFINITION
        # ------------------------------------------------------------------------------------------
        self.settings = read_settings_file()

        self.app = Flask(__name__)
        self.app.config['MAX_CONTENT_LENGTH'] = self.settings.get("MAX_CONTENT_LENGTH")

        # Enable the logging to file
        if not self.settings.get("DEBUG", True):
            try:
                handler = RotatingFileHandler(self.settings.get("LOG_FILE"), maxBytes=31457280, backupCount=5)
                handler.setLevel(logging.INFO)
                handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s : %(funcName)s - %(message)s'))
                self.app.logger.root.addHandler(handler)
            except Exception as e:
                print "Unable to open log file " + self.settings.get("LOG_FILE", "LOG FILE NOT SPECIFIED") + ". Error message: " + str(e)

        self.cache_instance = PySiCa(
            logger=self.app.logger,
            timeout=self.settings.get("TIMEOUT"),
            compress=self.settings.get("COMPRESS"),
            max_elems=self.settings.get("MAX_ELEMS"),
            clean_interval=self.settings.get("CLEAN_INTERVAL")
        )

        CORS(self.app, resources=r'/api/*')

        @self.app.route(self.settings.get("SERVER_SUBDOMAIN", "") + '/api/add', methods=['OPTIONS', 'POST'])
        def add():
            if request.method == "OPTIONS":
                return jsonify(True)

            element_id = request.json.get("element_id")
            data       = request.json.get("data")
            data_type  = request.json.get("data_type")
            user_id    = request.json.get("user_id", None)
            timeout    = request.json.get("timeout", None) # in minutes
            compress   = request.json.get("compress", None)

            success = self.cache_instance.add(element_id, data, data_type, timeout=timeout, compress=compress, user_id=user_id)

            return jsonify({'success': success, 'element_id' : element_id})

        @self.app.route(self.settings.get("SERVER_SUBDOMAIN", "") + '/api/get/', methods=['OPTIONS', 'GET'])
        @self.app.route(self.settings.get("SERVER_SUBDOMAIN", "") + '/api/get/<path:element_id>', methods=['OPTIONS', 'GET'])
        def get(element_id=None):
            if request.method == "OPTIONS":
                return jsonify(True)

            data_type = request.args.get('data_type', default=None)
            user_id   = request.args.get('user_id', default=None)
            reset_timeout = request.args.get('reset_timeout', default=False)
            timeout   = request.args.get('timeout', default=None)

            result = self.cache_instance.get_elem(element_id, data_type=data_type, user_id=user_id, reset_timeout=reset_timeout, timeout=timeout)

            if len(result) > 0:
                return jsonify({'success': True, 'result': result})
            else:
                return jsonify({'success': False})

        @self.app.route(self.settings.get("SERVER_SUBDOMAIN", "") + '/api/remove/<path:element_id>', methods=['OPTIONS', 'DELETE'])
        def remove(element_id):
            if request.method == "OPTIONS":
                return jsonify(True)

            user_id = request.args.get('user_id', default=None)

            result = self.cache_instance.remove(element_id, user_id=user_id)
            return jsonify({'success': len(result) > 0, 'result': result})

        @self.app.route(self.settings.get("SERVER_SUBDOMAIN", "") + '/api/reset/<path:element_id>', methods=['OPTIONS', 'GET'])
        def reset_timeout(element_id):
            if request.method == "OPTIONS":
                return jsonify(True)

            timeout = request.args.get('timeout', default=None)
            user_id = request.args.get('user_id', default=None)

            result = self.cache_instance.reset_timeout(element_id, timeout=timeout, user_id=user_id)
            if result:
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': "Element " + element_id + " is not in cache."})

    def launch(self):
        # ------------------------------------------------------------------------------------
        # LAUNCH APPLICATION
        # ------------------------------------------------------------------------------------
        self.app.run(
            host=self.settings.get("SERVER_HOST_NAME", "0.0.0.0"),
            port=self.settings.get("SERVER_PORT_NUMBER", 4444),
            debug=self.settings.get("DEBUG", False),
            threaded=True, use_reloader=False
        )


def read_settings_file():
    conf_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf/server.cfg")
    logging_conf_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf/logging.cfg")
    # Copy the default settings
    if not os.path.isfile(conf_path):
        copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "default/server.default.cfg"), conf_path)
        copyfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "default/logging.default.cfg"), logging_conf_path)

    settings = {}
    if os.path.isfile(conf_path):
        config = json.load(open(conf_path))

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
