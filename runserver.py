#!/usr/bin/env python

"""
PySiCa, a simple Python Cache system

v0.1 December 2018
"""

try:
    from server import Application
except Exception as ex:
    from server.server import Application

if __name__ == "__main__":
    application = Application()
    application.launch()
