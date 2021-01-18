#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
This script gets all supported displays of Inkycal by looking up driver files
in the e-paper drivers filepath and prepares a dictionary named
displays for the web-ui.

For Inkycal project
Copyright by aceisace
"""
from inkycal.display import Display

all_displays = Display.get_display_names()
getsize = Display.get_display_size


displays = []

for display in all_displays:
  cur = {}
  if 'colour' in display:
    name = '.'.join(display.replace('epd_','').replace('_colour','').split('_in_')) +'"' + " colour"
  else:
    name = '.'.join(display.replace('epd_','').split('_in_')) + '"'
  if 'v2' in name:
    name = name.replace("_v2", '') + " v2"
  if 'v3' in name:
    name = name.replace("_v3", '') + " v3"

  size = str(getsize(display)).replace(', ','x').replace(')','px)')
  cur[display] = (f'{name} {size}')
  displays.append(cur)
  #print(f'Display: {name} size: {size}')
