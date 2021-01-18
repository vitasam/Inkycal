#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import sys
logging.basicConfig(stream=sys.stderr)

# add your project directory to the sys.path
project_home = '/var/www/inkycal_ui'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# import flask app but need to call it "application" for WSGI to work
from main import app as application  # noqa
