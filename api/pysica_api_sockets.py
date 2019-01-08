import socket
import json
from struct import unpack, pack


class SimpleCache:

    def __init__(self, socket_file=None, server="localhost", port=4444, buffer_size=4096):
        self.socket_file = socket_file
        self.server = server
        self.port = port
        self.buffer_size = buffer_size

    def add(self, element_id, data, data_type="object", timeout=None, compress=None, user_id=None):
        return cache_add(element_id, data, data_type, timeout, compress, user_id, socket_file=self.socket_file, server=self.server, port=self.port, buffer_size=self.buffer_size)

    def get(self, element_id=None, data_type=None, user_id=None, reset_timeout=False, timeout=None):
        return cache_get(element_id, data_type, user_id, reset_timeout, timeout, socket_file=self.socket_file, server=self.server, port=self.port, buffer_size=self.buffer_size)

    def remove(self, element_id, user_id=None, return_elem=False):
        return cache_remove(element_id, user_id=user_id, return_elem=return_elem, socket_file=self.socket_file, server=self.server, port=self.port, buffer_size=self.buffer_size)

    def reset(self, element_id=None, timeout=None, user_id=None):
        return cache_reset(element_id, timeout=timeout, user_id=user_id, socket_file=self.socket_file, server=self.server, port=self.port, buffer_size=self.buffer_size)


def cache_add(element_id, data, data_type, timeout=None, compress=None, user_id=None, socket_file=None, server="localhost", port=4444, buffer_size=4096):
    try:
        cp = SocketHandler()
        cp.connect(socket_file, server, port)
        # Prepare package
        data = {
            'target': "add",
            'element_id': element_id,
            'data': data,
            'data_type': data_type,
            'timeout': timeout,
            'compress': compress,
            'user_id': user_id
        }
        # Send data
        response = cp.send_data(data, buffer_size=buffer_size)
        cp.close()
        return Response(json.loads(response))
    except:
        return Response({"success": False, "message": "Unable to connect to cache server."})


def cache_get(element_id=None, data_type=None, user_id=None, reset_timeout=False, timeout=None, socket_file=None, server="localhost", port=4444, buffer_size=4096):
    try:
        cp = SocketHandler()
        cp.connect(socket_file, server, port)
        # Prepare package
        data = {
            'target': "get",
            'element_id': element_id,
            'data_type': data_type,
            'user_id': user_id,
            'reset_timeout': reset_timeout,
            'timeout': timeout
        }
        # Get data
        response = cp.get_data(data, buffer_size=buffer_size)
        cp.close()
        return Response(json.loads(response))
    except:
        return Response({"success": False, "message": "Unable to connect to cache server."})


def cache_remove(element_id, user_id=None, return_elem=False, socket_file=None, server="localhost", port=4444, buffer_size=4096):
    try:
        # Get data
        if return_elem:
            element = cache_get(element_id=element_id, user_id=user_id, socket_file=socket_file, server=server, port=port, buffer_size=buffer_size)
        # Remove element
        cp = SocketHandler()
        cp.connect(socket_file, server, port)
        print("sadasds")
        # Prepare package
        data={
            'target': "remove",
            'element_id': element_id,
            'user_id': user_id
        }
        response = cp.send_data(data, buffer_size=buffer_size)
        response = json.loads(response)

        if return_elem:
            response["result"] = element.result

        cp.close()
        return Response(response)
    except:
        return Response({"success": False, "message": "Unable to connect to cache server."})


def cache_reset(element_id, timeout=None, user_id=None, socket_file=None, server="localhost", port=4444, buffer_size=4096):
    try:
        cp = SocketHandler()
        cp.connect(socket_file, server, port)
        # Prepare package
        data={
            'target': "reset",
            'element_id': element_id,
            'timeout': timeout,
            'user_id': user_id
        }
        # Get data
        response = cp.send_data(data, buffer_size=buffer_size)
        cp.close()
        return Response(json.loads(response))
    except:
        return Response({"success": False, "message": "Unable to connect to cache server."})


class SocketHandler:
    def __init__(self):
        self.socket = None

    def connect(self, socket_file=None, server_ip=None, server_port=None):
        if socket_file is not None:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(socket_file)
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server_ip, server_port))

    def close(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
        self.socket = None

    def send_data(self, data, buffer_size=4096):
        data = json.dumps(data)
        # use struct to make sure we have a consistent endianness on the length
        length = pack('>Q', len(data))
        # sendall to make sure it blocks if there's back-pressure on the socket
        self.socket.sendall(length)
        self.socket.sendall(data)
        # Receive respond
        bs = self.socket.recv(8)
        (data_length,) = unpack('>Q', bs)
        data = b''
        while len(data) < data_length:
            # doing it in batches is generally better than trying
            # to do it all in one go, so I believe.
            to_read = data_length - len(data)
            data += self.socket.recv(buffer_size if to_read > buffer_size else to_read)
        return data

    def get_data(self, data, buffer_size=4096):
        data = json.dumps(data)
        # use struct to make sure we have a consistent endianness on the length
        length = pack('>Q', len(data))
        # sendall to make sure it blocks if there's back-pressure on the socket
        self.socket.sendall(length)
        self.socket.sendall(data)
        # Receive respond
        bs = self.socket.recv(8)
        (data_length,) = unpack('>Q', bs)
        data = b''
        while len(data) < data_length:
            # doing it in batches is generally better than trying
            # to do it all in one go, so I believe.
            to_read = data_length - len(data)
            data += self.socket.recv(buffer_size if to_read > buffer_size else to_read)
        return data


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


