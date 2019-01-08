# Table of contents
<!--ts-->
   * [Table of contents](#table-of-contents)
   * [Introduction](#introduction)
   * [Features](#features)

<!--te-->

# Introduction
PySiCa (_Python Simple Cache_) is a simple cache system implemented for Python applications.
A cache is a component that stores data so that future requests for that data can be served faster; the data stored in a cache might be the result of an earlier computation or a copy of data stored elsewhere.

# How to install
PySiCa has few requirements that can be easily installed using pip has follows:
```bash
 pip install -f requirements
```

Installing the Falcon wheel is a great way to get up and running quickly in a development environment, but for an extra speed boost when deploying your application in production, Falcon can compile itself with Cython.
```bash
 pip install cython
 pip install ujson
 pip install APScheduler
 pip install --no-cache-dir --no-binary :all: falcon
 pip install --no-cache-dir https://github.com/unbit/uwsgi/archive/uwsgi-2.0.zip#egg=uwsgi
```

# Features
PySiCa is entirely implemented in Python and provides the following features:
- Easy to use and to install in your application.
- Available as a module imported in your application or as a self-contained service accessible through API calls.
  - Using RESTful API + a high-performance web server
  - Using pure HTTP or file-based sockets     
- It doesn't depend on other libraries or tools.
- Lightweight module. The code takes less than 300 lines of code.
- Dockerized version available

# Using PySiCa as a self-contained webserver
Coming soon...
