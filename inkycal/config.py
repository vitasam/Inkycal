#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Configuration file for Inkycal Project
Handles variables for both the web-ui and Inkycal core
Do not change unless you know what you are doing.

Copyright by aceisace
"""

from os.path import abspath

def directory_up(levels):
  current_path = abspath(__file__)
  return "/" + "/".join(current_path.split("/")[1:][:-levels]) + "/"

config = {
  # Logfile
  "LOGGING_PATH": directory_up(2) + "logs/inkycal.log",

  # External content
  "FONT_DIR": directory_up(2) + "external/fonts/",
  "IMAGE_DIR": directory_up(2) + "external/images/",
  "ICAL_DIR" : directory_up(2) + "external/icalendars/",

  # Entry-point for uploads or external content
  "UPLOAD_PATH": directory_up(2)+"external/",

  
  # Path for temporary content
  "TEMP_DIR": directory_up(2) + "images/",

  # Path for E-Paper drivers
  "DRIVER_DIR": directory_up(1) + "display/drivers/",


  # Path for Inykcal run file
  "INKYCAL_RUNFILE": directory_up(2)+"inkyrun.py",

  # Settings path
  "SETTINGS_PATH": directory_up(3)+"settings.json"
  }
