"""
PySiCa, a simple Python Cache system

v0.2 December 2018
"""

import datetime
import marshal
# import psutil
import uuid
import logging
import atexit
from sys import getsizeof
from apscheduler.schedulers.background import BackgroundScheduler


class Singleton(type):
    """
    The Singleton definition of the queue.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PySiCa:

    __metaclass__ = Singleton

    # Implementation of the singleton interface
    def __init__(self, timeout=10, compress=True, max_elems=50, clean_interval=30, logger=None):
        self.id = uuid.uuid4()
        self.general_cache = dict()
        self.user_cache = dict()
        if logger is None:
            self.logger = logging.getLogger('queue_application')
        else:
            self.logger = logger
        # Set default options
        self.options = {
            "timeout": timeout, # TODO USE -1 TO DISABLE
            "compress": compress,
            "max_elems": max_elems, # TODO NOT USED
            "clean_interval": clean_interval
        }
        # SCHELUDE THE CLEANING TASK
        self.logger.debug("A new instance for MemCacheManager was created (id: " + str(self.id) + ")...")
        self.start_schelude_tasks()

    def add(self, element_id, data, data_type, timeout=None, compress=None, user_id=None):
        try:
            if timeout is None:
                timeout = self.options.get("timeout", 10)
            if compress is None:
                compress = self.options.get("compress", True)

            self.logger.info("Storing new element in cache " + str(self.id) + (" (compressed)" if compress else "") + (" for user " + user_id if user_id is not None else ""))
            # Choose which cache should be used
            cache = self.get_cache(user_id)
            # Store the object in the corresponding cache
            cache[str(element_id)] = {
                "timeout": datetime.datetime.now() + datetime.timedelta(minutes=timeout),
                "compressed": compress,
                "data_type" : data_type,
                "data": marshal.dumps(data) if compress else data
            }
            # Print the memory usage
            self.print_memory_usage()
            return True
        except Exception as e:
            self.logger.error("Unable to add new element to cache " + str(self.id) + ": " + str(e))
            return False

    def get_elem(self, element_id=None, data_type=None, user_id=None, reset_timeout=False, timeout=None):
        # Choose which cache should be used
        cache = self.get_cache(user_id)
        result = []
        if element_id is not None and element_id in cache:
            elem = cache.get(element_id)
            if reset_timeout:
                self.reset_timeout(element_id, timeout=timeout, user_id=user_id)
            result.append(marshal.loads(elem.get("data")) if elem.get("compressed") else elem.get("data"))
        elif data_type is not None:
            for element_id in cache:
                elem = cache.get(element_id)
                if elem.get("data_type") == data_type:
                    if reset_timeout:
                        self.reset_timeout(element_id, timeout=timeout, user_id=user_id)
                    result.append({"id": element_id, "data": marshal.loads(elem.get("data")) if elem.get("compressed") else elem.get("data")})
        return result

    def remove(self, element_id, user_id=None):
        # Choose which cache should be used
        cache = self.get_cache(user_id)
        # Get the element
        result = self.get_elem(element_id, user_id=user_id)
        if len(result) > 0:
            self.logger.info("Deleting element from cache " + str(self.id) + " (element id: " + str(element_id) + ")")
            del cache[element_id]
        # Print the memory usage
        self.print_memory_usage()
        # Return the removed element
        return result

    def reset_timeout(self, element_id, timeout=None, user_id=None):
        if timeout is None:
            timeout = self.options.get("timeout", 10)

        try:
            timeout = int(timeout)
            # Choose which cache should be used
            cache = self.get_cache(user_id)
            if str(element_id) in cache:
                self.logger.info("Resetting timeout for element " + element_id + " in cache "+ str(self.id) + (" for user " + user_id if user_id is not None else ""))
                cache.get(element_id)["timeout"] = datetime.datetime.now() + datetime.timedelta(minutes=timeout)
                return True
            else:
                self.logger.info("Element " + element_id + " not found in cache " + str(self.id) + (" for user " + user_id if user_id is not None else ""))
                return False
        except:
            return False

    def clean_cache(self):
        self.logger.debug("Cleaning cache " + str(self.id))
        self.options["n_iteration"] = self.options.get("n_iteration", 0) + 1
        now = datetime.datetime.now()
        # First clean the values for the general cache
        keys = list(self.general_cache.keys())
        for key in keys:
            if self.general_cache.get(key).get("timeout") < now:
                self.logger.info("Removing item " + str(key) + " from cache " + str(self.id))
                del self.general_cache[key]
        # Now clean the cache for each user
        user_ids = list(self.user_cache.keys())
        for user_id in user_ids:
            cache = self.user_cache.get(user_id)
            keys = list(cache.keys())
            for key in keys:
                if cache.get(key).get("timeout") < now:
                    self.logger.info("Removing item " + str(key) + " from " + user_id + "'s cache " + str(self.id))
                    del cache[key]
            if len(cache) == 0:
                del self.user_cache[user_id]
        # Print the memory usage
        level="debug"
        if self.options.get("n_iteration") > 10:
            del self.options["n_iteration"]
            level = "info"
        self.print_memory_usage(level=level)

    def get_cache_size(self):
        # First get the total size
        size = 0
        for value in self.general_cache.values():
            size += getsizeof(value.get("data"))
        for user_id in self.user_cache:
            cache = self.user_cache.get(user_id)
            for value in cache.values():
                size += getsizeof(value.get("data"))
        # Now convert to human readable
        step_to_greater_unit = 1024.
        size = float(size)
        unit = 'bytes'

        if (size / step_to_greater_unit) >= 1:
            size /= step_to_greater_unit
            unit = 'KB'
        if (size / step_to_greater_unit) >= 1:
            size /= step_to_greater_unit
            unit = 'MB'
        if (size / step_to_greater_unit) >= 1:
            size /= step_to_greater_unit
            unit = 'GB'
        if (size / step_to_greater_unit) >= 1:
            size /= step_to_greater_unit
            unit = 'TB'

        precision = 1
        size = round(size, precision)
        return str(size) + ' ' + unit

    def get_ram_usage(self):
        return ""
        # return str(psutil.virtual_memory().percent) + "%"

    def print_memory_usage(self, level="debug"):
        message = "Status for cache " + str(self.id) + ": Size is " + self.get_cache_size()
        # + ", RAM usage " + self.get_ram_usage()
        if level == "info":
            self.logger.info(message)
        else:
            self.logger.debug(message)

    def get_cache(self, user_id):
        if user_id is not None:
            self.user_cache[user_id] = self.user_cache.get(user_id, {})  # Initialize if not present
            return self.user_cache.get(user_id)
        else:
            return self.general_cache

    def set_option(self, key, value):
        self.options[key] = value

    def set_logger(self, logger):
        self.logger = logger

    def start_schelude_tasks(self):
        self.logger.info("Scheduling clean_cache for cache " + str(self.id))

        cron = BackgroundScheduler(daemon=True)
        try:
            logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
            logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)
            logging.getLogger('apscheduler.jobstores.default').setLevel(logging.WARNING)
        except:
            pass

        # Explicitly kick off the background thread
        cron.start()

        # @cron.interval_schedule(seconds=1)
        def schelude_task():
            self.clean_cache()

        cron.add_job(schelude_task, trigger='interval', seconds=self.options.get("clean_interval", 30), id='clean_cache_job')
        # Shutdown your cron thread if the web process is stopped
        atexit.register(lambda: cron.shutdown(wait=False))
