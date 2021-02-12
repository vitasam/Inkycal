from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

__project__ = "inkycal"
__version__ = "2.0.1"
__description__ = "Inkycal is a python3 software for syncing icalendar events, weather and news on selected E-Paper displays"
__packages__ = ["inkycal"]
__author__ = "aceisace"
__author_email__ = "aceisace63@yahoo.com"
__url__ = "https://github.com/aceisace/Inkycal"

__install_requires__ = ['Pillow>=7.1.1',                  # Images
                        'arrow>=0.15.6',                  # Time handling
                        'icalendar==4.0.6',               # iCalendar parsing
                        'recurring-ical-events==0.1.17b0',# Agenda/Calendar module
                        'pyowm==3.1.1',                   # Weather module
                        'feedparser==5.2.1',              # Feeds module
                        'todoist-python==8.1.2',          # Todoist module
                        'yfinance==0.1.55',               # Stocks stocks
                        'matplotlib==3.3.4',              # Stocks module
                        #'numpy>=1.18.2',                  # image pre-processing -> removed for issues with rpi os
                        ]

__classifiers__ = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Intended Audience :: Education",
    "Natural Language :: English",
    "Programming Language :: Python :: 3 :: Only",
]

                
setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    author = __author__,
    author_email  = __author_email__,
    url = __url__,
    install_requires = __install_requires__,
    classifiers = __classifiers__,
    long_description=long_description,
    long_description_content_type='text/markdown',
)
