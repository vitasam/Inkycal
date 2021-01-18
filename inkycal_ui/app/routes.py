import json
import imghdr
import os
import re
from subprocess import run, check_output
from PIL import Image

from flask import render_template, flash, redirect, request, Response, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename
from app import app, db
from app.forms import GenericForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

from inkycal import Display
from .config_loader import get_all_config
from .parser import load_settings
from .timezone_helper import get_continents, get_countries, current_tz
from .supported_displays import displays

settings_path = app.config['SETTINGS_PATH']
log_path = app.config['LOGGING_PATH']
inkycal_runpath = app.config['INKYCAL_RUNPATH']

modules_config = get_all_config()

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

# Home
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = GenericForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = True if request.form.get('remember_me') == "on" else False

        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=remember_me)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

# Change password
@login_required
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    form = GenericForm()
    if form.validate_on_submit():
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        user = User.query.all()[0]
        if not user.check_password(current_password):
            flash('Invalid password')
            return redirect(url_for('change_password'))
        elif new_password != confirm_password:
            flash('New passwords do not match')
            return redirect(url_for('change_password'))
        elif current_password == new_password:
            flash('A new password must be different from the current one')
            return redirect(url_for('change_password'))
        elif len(new_password) < 8 or re.search('[0-9]', new_password) is None or re.search('[A-Z]', new_password) is None:
            flash('The new password is not strong enough. Please check the password requirements')
            return redirect(url_for('change_password'))
        else:
            user.set_password(new_password)
            db.session.commit()
            logout_user()
            flash('password changed successfully. Please login with new details')
            return redirect(url_for('login'))

    return render_template('change_password.html', title='change password', form=form)

# Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('you have logged out')
    return redirect(url_for('index'))


# Wifi-setup
@app.route('/setup_wifi')
def wifi_setup():
    return render_template('wifi.html', title='Wifi-setup')

# SSH file
@app.route('/create_ssh')
def create_ssh():
    return render_template('create_ssh.html', title='SSH file generator')


# Inkycal-setup
@login_required
@app.route('/inkycal-config', methods=['GET', 'POST'])
def inkycal_config():

    # Form
    form = GenericForm()

    # Get config of all modules
    modules_config = get_all_config()

    # Load previous settings
    current_config = load_settings(settings_path)

    # File not Found
    if current_config == 0:
        flash('no settings file found')

    # File found, but empty or incorrect
    elif current_config == 1:
        flash('Settings file found, but could not be parsed. Please try creating a new file')

    # Unexpected problem when parsing
    elif current_config == 2:
        flash('Error when attempting to load settings file')

    if form.validate_on_submit():

        # General epaper settings
        model = request.form.get('model')
        update_interval = int(request.form.get('update_interval'))
        calibration_hour_1 = int(request.form.get('calibration_hour_1'))
        calibration_hour_2 = int(request.form.get('calibration_hour_2'))
        calibration_hour_3 = int(request.form.get('calibration_hour_3'))
        orientation: int(request.form.get('orientation'))
        language = request.form.get('language')
        
        # if the info section checkbox is checked, it can be found in the form.get function
        info_section = True if request.form.get('info_section') else False

        info_height = int(request.form.get('info_section_height')) if info_section == True else None

        # template for basic settings
        template = {
            "model": model,
            "update_interval": update_interval,
            "orientation": int(request.form.get('orientation')),
            "info_section": info_section,
            "info_section_height": info_height,
            "calibration_hours": [calibration_hour_1, calibration_hour_2, calibration_hour_3],
            "modules": [],
            }


        # common module config (shared by all modules)
        padding_x = int(request.form.get('padding_x'))
        padding_y = int(request.form.get('padding_y'))
        fontsize = int(request.form.get('fontsize'))
        language = request.form.get('language')

        common_settings = {"padding_x":padding_x, "padding_y":padding_y, "fontsize":fontsize, "language":language}

        # loop over the modules, add their config data based on user selection, merge the common_settings into each module's config
        no_of_modules = int(request.form.get("module_counter"))

        # display size ---- Since Inkycal works in vertical mode (only), the width and height have to be flipped here
        display_size = Display.get_display_size(model) # returns width,height but flipping these for vertical mode
        height, width = int(display_size[0]), int(display_size[1])

        # If info section was active, substract the height of the info section from the display height
        if info_section == True:
            height -= info_height

        # get all module heights, calculate single part
        module_sizes = [int(request.form.get(f"module{i}_height")) for i in range(1, no_of_modules+1)]

        if sum(module_sizes) != 0:
            single_part = height / sum(module_sizes)

        for i in range(1, no_of_modules+1):
            conf = {}
            module = f'selected_module{i}'

            if request.form.get(module) != "None":
                #conf = {"position":i , "name": request.form.get(module), "config":{}}
                conf = {"name": request.form.get(module), "config":{}}

                for modules in modules_config:
                    if modules['name'] == request.form.get(module):

                        module_height = int( request.form.get(f"module{i}_height") )
                        conf['ratio'] = module_height
                        conf['config']['size'] = (width, int(single_part*module_height) )

                        # Add required fields to the config of the module in question
                        # True/False choices are converted to string for some reason, leading to incorrect values
                        # Convert "True" to True, "False" to False and empty input to None
                        if 'requires' in modules:
                            for key in modules['requires']:
                                val = request.form.get(f'module{i}_{key}').replace(" ", "")
                                if val == "True":
                                    val = True
                                elif val == "False":
                                    val = False
                                elif val == "":
                                        val = None
                                conf['config'][key] = val

                        # For optional fields, check if user entered/selected something. If not, and a default value was given,
                        # use the default value, else set the value of that optional key as None
                        # True/False choices are converted to string for some reason, leading to incorrect values
                        # Convert "True" to True, "False" to False and empty input to None
                        if 'optional' in modules:
                            for key in modules['optional']:
                                if request.form.get(f'module{i}_{key}'):
                                    val = request.form.get(f'module{i}_{key}').replace(" ", "")
                                    if val == "True":
                                        val = True
                                    elif val == "False":
                                        val = False
                                    elif val == "":
                                        val = None
                                    conf['config'][key] = val
                                else:
                                    if "default" in modules["optional"][key]:
                                        conf['config'][key] = modules["optional"][key]["default"]
                                    else:
                                        conf['config'][key] = None

                # update the config dictionary
                conf["config"].update(common_settings)
                template['modules'].append(conf)

        # Save the settings file in the specified path
        try:
            # Save the generated file at the correct path (using the path from the parser)
            with open(settings_path, mode='w') as settings_file:
                json.dump(template, settings_file, indent=4)

            flash("Settings file updated successfully. Please restart inkycal to apply changes")

        # If something unexpected happened
        except:
            flash('Something unexpted happened when saving the settings file')

    return render_template('inkycal-config2.html', title='Inkycal-Setup', conf=modules_config, form=form, 
    current_config=current_config, supported_displays=displays)

# Inkycal-setup
@login_required
@app.route('/control-panel', methods=['GET', 'POST'])
def control():
    form = GenericForm()
    data = 0

    def check_state():
        try:
            command = "sudo service supervisor status Inkycal".split()
            state = str(check_output(command))
            if "Active: active (running)" in state:
                return 1
        except:
            return 0

    if form.validate_on_submit():
        pressed = request.form.get('pressed')

        # handle restart, start and stop of Inykcal
        if pressed in ["restart", "start", "stop"]:
            command = run(f'sudo service supervisor {pressed} Inkycal'.split())
            response = command.returncode
            if response == 0:
                flash(f'Inkycal {pressed}..success')
            else:
                flash(f'Could not {pressed} Inkycal')


        # Show log, settings, or errors
        elif pressed == "show_settings":
            try:
                with open(settings_path, mode='r') as file:
                    data = file.readlines()
            except FileNotFoundError:
                flash('No settings file found')
                

        elif pressed == "show_log":
            try:
                with open(f'{log_path}', mode='r') as file:
                    data = file.readlines()[-100:]
            except FileNotFoundError:
                flash('No log file found')

        elif pressed == 'clear_log':
            command = run(f'rm {log_path}'.split())
            response = command.returncode
            if response == 0:
                flash(f'Cleared log file')
            else:
                flash('Could not clear log file')
                
        elif pressed == 'show_server_log':
            try:
                with open(f'/var/log/apache2/error.log', mode='r') as file:
                    data = file.readlines()[-50:]
            except FileNotFoundError:
                flash('No log file found')

    return render_template('control.html', title='Control', form=form, status=check_state(), data=data )


# Timezone
@login_required
@app.route('/timezone', methods=['GET', 'POST'])
def timezone():
    form = GenericForm()
    flash(f'current timezone: {current_tz()}')

    data = {}
    data['continents'] = get_continents()

    if form.validate_on_submit():
        if request.form.get('continent') and not request.form.get('country'):
            continent = request.form.get('continent')
            data['countries'] = get_countries(continent)
            data['prev_continent'] = request.form.get('continent')
            return render_template('timezone.html', title='Set timezone', form=form, data=data)

        elif request.form.get('continent') and request.form.get('country'):
            continent, country = request.form.get('continent'), request.form.get('country')
            data['countries'] = get_countries(continent)
            data['prev_continent'] = continent
            data['prev_country'] = country

            timezone = f"{continent}/{country}"
            command = run(f"sudo timedatectl set-timezone {timezone}".split())
            response = command.returncode
            if response == 0:
                flash(f'timezone updated successfully. New timezone: {timezone}')
            else:
                flash('timezone could not be updated!')

    return render_template('timezone.html', title='Set timezone', form=form, data= data)


# Display test
@login_required
@app.route('/test-display', methods=['GET', 'POST'])
def test_display():
    form = GenericForm()

    if form.validate_on_submit():
        test_im_path = "/home/pi/Inkycal/Gallery/coffee.png"
        model = request.form.get('model')
        size = Display.get_display_size(model)
        im = Image.open(test_im_path).rotate(90, expand=True).convert('RGBA')
        canvas = Image.new('RGB', size, color = 'white')
        im_colour = Image.new('RGB', size, color = 'white')
        x = int( (size[0]- im.size[0]) /2)
        y = int( (size[1]- im.size[1]) /2)
        canvas.paste(im, (x,y), im)

        display = Display(model)
        display.render_with_timeout(canvas, im_colour=im_colour)
        flash('If you see an image, the test was successful. If not, please check your wiring and the model')

    return render_template('display-test.html', title='Inkycal display test', form=form, supported_displays=displays)


# Uploader
@login_required
@app.route('/uploads', methods=['GET', 'POST'])
def uploads():
    form = GenericForm()
    
    # Get all files from upload directory
    files = os.listdir(app.config['UPLOAD_PATH'])
    
    image_files = [img for img in files if img.split('.')[-1].lower() in ('jpg','png','jpeg')]
    
    icalendars = [ical for ical in files if ical.split('.')[-1].lower() == 'ics']

    # Create a dictionary mapping each image file with it's orientation -> horizontal, vertical
    # If the file is not an image, use None
    images = {}
    for im in image_files:
        with Image.open(f"{app.config['UPLOAD_PATH']}/{im}") as img: 
            size = img.size
        images[im] = 'horizontal' if size[0] > size[1] else 'vertical'

    # Parse incoming request
    if request.method == 'POST':
        if request.form.get('selection'):
            selection = request.form.get('selection').split(' ')
            selection.remove("")

            for files in selection:
                filepath = f"{app.config['UPLOAD_PATH']}/{files}"
                if os.path.exists(filepath):
                    os.remove(filepath)
                else:
                    flash("some files could not be deleted")
        
        
        if 'file' in request.files:
            uploaded_files = request.files.getlist('file')

            for uploaded_file in uploaded_files:
                filename = secure_filename(uploaded_file.filename)
                if filename != '':
                    file_ext = os.path.splitext(filename)[1]
                    if file_ext.lower() not in app.config['UPLOAD_EXTENSIONS']:
                        return "Unsupported format", 400
                    
                    # problematic on Apple Camera roll
                    # if file_ext != validate_image(uploaded_file.stream):
                    #    return "Invalid file", 400
                    uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

        return redirect(url_for('uploads'))

    return render_template('uploads.html', title='Inkycal uploader', form=form, images=images, icalendars=icalendars)

# Uploaded files viewer
@login_required
@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

