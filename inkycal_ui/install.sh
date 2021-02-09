#!/bin/bash

# install flask and flask-extensions
pip3 install -r requirements.txt

# install apache2 and dependencies
xargs -a packages.txt sudo apt-get install -y

# copy apache2 conf file to correct location
sudo cp inkycal.conf /etc/apache2/sites-available/

# disable currently active site
sudo a2dissite 000-default.conf

# enable inkycal site
sudo a2ensite inkycal.conf

# Add shortcut (symbolic link) of web-ui in /var/www
cd ..
sudo ln -s /home/$USER/Inkycal/inkycal_ui /var/www

# update changes
sudo systemctl restart apache2