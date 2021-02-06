import os
basedir = os.path.abspath(os.path.dirname(__file__))

from inkycal.config import config as inkycal_config

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '!nkycal_is_awes*me!^_^'

##    SETTINGS_PATH = '/home/pi/settings.json'
##    LOGGING_PATH = '/var/www/inkycal_ui/app/logs/logs.log'
##    INKYCAL_RUNPATH = '/var/www/inkycal_ui/app/inkyrun.py'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 1024 * 1024 * 16
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.jpeg', '.ics', '.ttf', '.otf']    
    UPLOAD_PATH = inkycal_config['UPLOAD_PATH']
