#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Inkycal load_eternal function

Allows automatic import of files from their filename if they are
in one of the specified folders by the config file

Copyright by aceisace
"""
from inkycal.config import config
from os import listdir

def load_external(filename):
  """Returns the filepath of the filename in the external content folder.

  Checks the file-extension to determine which subfolder to look for.
  Checks if file could be found 

  Returns:
    - String of filepath if file could be found.

  Raises:
    - FileNotFoundError if file could not be found.
    - TypeError if the file extension is not supported
    
  """
  
  extension = filename.split('.')[-1].lower()

  # look for iCalendar files in iCalendar folder
  if extension == "ics":
    if filename in listdir(config['ICAL_DIR']):
      return f"{config['ICAL_DIR']}/{filename}"
    else: raise FileNotFoundError("File not found")

  # Look for font files in the font folder
  elif extension in ("otf", "ttf"):
    if filename in listdir(config['FONT_DIR']):
      return f"{config['FONT_DIR']}/{filename}"
    else: raise FileNotFoundError("File not found")

  # Look for image files in the image folder
  elif extension in ("png", "jpg", "jpeg"):
    if filename in listdir(config['IMAGE_DIR']):
      return f"{config['IMAGE_DIR']}/{filename}"
    else: raise FileNotFoundError("File not found")

  else:
    raise TypeError("Unsupported file format")
    
  
