import json

def load_settings(path):
  """loads and parse settings from given path

  This loads the settings file from the specified path, converts it so the
  web-ui can understand it's data. The

  """
  try:
    # Try to open the settings file
    with open(path) as settings_file:
      settings = json.load(settings_file)

  # If the file was not found, return 0
  except FileNotFoundError:
    print('No settings file could be found in the specified location')
    return 0

  except ValueError:
    print('File could not be parsed')
    return 1
    
  # If something unexpected happened, return 1
  except Exception as Error:
    print('An unknown error occured when attempting to parse the settings file')
    return 2


  # format calibration hours
  for hour in range(len(settings['calibration_hours'])):
    settings[f'calibration_hour_{hour+1}'] = settings['calibration_hours'][hour]
  del settings['calibration_hours']

  # format value of info section
  if settings['info_section'] == True:
    settings['info_section'] = 1
  else:
    settings['info_section'] = 0

  # Parse common config from first module in settings file
  try:
    first = settings['modules'][0]['config']
    settings['language'] = first['language']
    settings['fontsize'] = first['fontsize']
    settings['padding_y'] = first['padding_y']
    settings['padding_x'] = first['padding_x']
  except:
    print('no module in settings found')
    pass

  counter = 1
  mod = {}
  modules = settings['modules']
  for module in modules:
    for conf in module['config']:
      if conf not in ('size', 'padding_x', 'padding_y','fontsize', 'language'):
        if module['config'][conf] == True:
          val = 'True'
        elif module['config'][conf] == False:
          val = 'False'
        else:
          val = module['config'][conf]
        mod[f'module{counter}_{conf}'] = val
    mod[f'module{counter}_height'] = module['ratio']
    del module['config']
    counter += 1
    

  settings['prev_input'] = mod
  # return settings
  return json.dumps(settings)
