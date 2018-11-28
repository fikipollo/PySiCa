"""
PySiCa, a simple Python Cache system

v0.2 December 2018
"""

import requests
import json


class SimpleCache:

    def __init__(self, server="localhost", port=4444, protocol="http"):
        self.server = server
        self.port = port
        self.protocol = protocol

    def add(self, element_id, data, data_type="object", timeout=None, compress=None, user_id=None):
        return cache_add(element_id, data, data_type, timeout, compress, user_id, server=self.server, port=self.port, protocol=self.protocol)

    def get(self, element_id=None, data_type=None, user_id=None, reset_timeout=False, timeout=None):
        return cache_get(element_id, data_type, user_id, reset_timeout, timeout, server=self.server, port=self.port, protocol=self.protocol)

    def remove(self, element_id, user_id=None, return_elem=False):
        return cache_remove(element_id, user_id=user_id, server=self.server, port=self.port, protocol=self.protocol, return_elem=return_elem)

    def reset(self, element_id=None, timeout=None, user_id=None):
        return cache_reset(element_id, timeout=timeout, user_id=user_id, server=self.server, port=self.port, protocol=self.protocol)


def cache_add(element_id, data, data_type, timeout=None, compress=None, user_id=None, server="localhost", port=4444, protocol="http"):
    try:
        server = protocol + "://" + server.replace(protocol + "://", "").rstrip("/") + ":" + str(port)
        response = requests.post(server + "/api/add", json={
            'element_id': element_id,
            'data': data,
            'data_type': data_type,
            'timeout': timeout,
            'compress': compress,
            'user_id': user_id
        })
        return Response(json.loads(response.text))
    except:
        return Response({"success": False, "message": "Unable to connect to cache server."})


def cache_get(element_id=None, data_type=None, user_id=None, reset_timeout=False, timeout=None, server="localhost", port=4444, protocol="http"):
    try:
        server = protocol + "://" + server.replace(protocol + "://", "").rstrip("/") + ":" + str(port)

        url = server + "/api/get"
        if element_id is not None:
            url+= "/" + element_id

        extra = ""
        extra += ("&data_type=" + data_type if data_type else "")
        extra += ("&user_id=" + user_id if user_id else "")
        extra += ("&reset_timeout=1" if reset_timeout else "")
        extra += ("&timeout=" + str(timeout) if timeout else "")

        if extra != "":
            extra = "?" + extra[1:]
            url += extra

        response = requests.get(url)
        return Response(json.loads(response.text))
    except:
        return Response({"success": False, "message": "Unable to connect to cache server."})


def cache_remove(element_id, user_id=None, server="localhost", port=4444, protocol="http", return_elem=False):
    try:
        server = protocol + "://" + server.replace(protocol + "://", "").rstrip("/") + ":" + str(port)

        url = server + "/api/remove/" + element_id

        extra = ""
        extra += ("&user_id=" + user_id if user_id else "")
        extra += ("&return=1" if return_elem else "")

        if extra != "":
            extra = "?" + extra[1:]
            url += extra

        response = requests.delete(url)
        return Response(json.loads(response.text))
    except:
        return Response({"success": False, "message": "Unable to connect to cache server."})


def cache_reset(element_id, timeout=None, user_id=None, server="localhost", port=4444, protocol="http"):
    try:
        server = protocol + "://" + server.replace(protocol + "://", "").rstrip("/") + ":" + str(port)

        url = server + "/api/reset/" + element_id

        extra = ""
        extra += ("&user_id=" + user_id if user_id else "")
        extra += ("&timeout=" + str(timeout) if timeout else "")

        if extra != "":
            extra = "?" + extra[1:]
            url += extra

        response = requests.put(url)
        return Response(json.loads(response.text))
    except:
        return Response({"success": False, "message": "Unable to connect to cache server."})


class Response(object):
    def __init__(self, json_object):
        if "success" in json_object:
            self.success = json_object.get("success")
        if "element_id" in json_object:
            self.element_id = json_object.get("element_id")
        if "result" in json_object:
            self.result = json_object.get("result")
        if "message" in json_object:
            self.message = json_object.get("message")

    def __str__(self):
        _str = dict()
        try:
            _str["success"] = self.success
        except:
            pass
        try:
            _str["element_id"] = self.element_id
        except:
            pass
        try:
            _str["result"] = self.result
        except:
            pass
        try:
            _str["message"] = self.message
        except:
            pass
        return str(_str)

    def __repr__(self):
        return self.__str__()
