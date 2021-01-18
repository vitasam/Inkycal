import glob, os

tz_path = '/usr/share/zoneinfo/'

def get_continents():
  files = [f.split('/')[-1].split('.')[0] for f in
           glob.glob(f"{tz_path}*") if os.path.isdir(f)]

  files.remove('posix')
  files.remove('right')
  files.sort()

  return files


def get_countries(continent):
  files = [f.split('/')[-1].split('.')[0] for f in
           glob.glob(f"{tz_path}/{continent}/*")]
  files.sort()
  return files


def current_tz():
  with open("/etc/timezone") as file:
    cur_tz = file.readline()
  return cur_tz
