import os
from flask import render_template, safe_join, send_from_directory, request, Flask, redirect, url_for
from wtforms import Form, TextField, TextAreaField, validators
from plot_service import app
from plot_service.exceptions import InvalidUsage

TERRAREF_BASE='/projects/arpae/terraref'


def check_site(site):

    terraref = os.environ.get('TERRAREF_BASE', TERRAREF_BASE)
    if not os.path.exists(terraref):
       raise InvalidUsage('Could not find TerraREF data, try setting '
                          'TERRAREF_BASE environmental variable')

    sitepath = safe_join(terraref, 'sites', site)
    if not os.path.exists(sitepath):
        raise InvalidUsage('unknown site', payload={'site':site})

    return sitepath

def check_sensor(site, sensor, date=None):
    """check for valid sensor with optional date """

    sitepath = check_site(site)

    sensorpath = safe_join(sitepath, 'Level_1', sensor)
    if not os.path.exists(sensorpath):
        raise InvalidUsage('unknown sensor', 
                payload={'site':site, 'sensor': sensor})

    if not date:
        return sensorpath

    datepath = safe_join(sensorpath, date)
    print("datepath = {}".format(datepath))
    if not os.path.exists(datepath):
        raise InvalidUsage('sensor data not available for given date',
                payload={'site':site, 'sensor':sensor, 'date':date})

    return datepath


def get_sensor_product(site, sensor):
    """Returns the downloadable product for each site-sensor pair"""

    # TODO do something much more intelligent
    return "ff.tif"


def get_attachment_name(site, sensor, date, product):
    """Encodes site, sensor, and date to create a unqiue attachment name"""

    root, ext = os.path.splitext(product)
    return "{}-{}-{}.{}".format(site, sensor, date, ext)


@app.route('/api/v1/sites/<site>/sensors/<sensor>/<date>')
def sensor(site, sensor, date):
    """Return a downloaded version of the sensor """

    # maps from site and sensor to a filename that should be
    # available for every date
    product = get_sensor_product(site, sensor)

    datepath = check_sensor(site, sensor, date)
    path = os.path.join(datepath, product)
    if not os.path.exists(path):
        raise InvalidUsage('sensor data not available for given date',
                payload={'site':site, 'sensor':sensor, 'date':date})

    # encodes site, sensor, date into attachment filename
    attachment_filename = get_attachment_name(site, sensor, date, product)

    return send_from_directory(datepath, product, as_attachment=True,
                               attachment_filename=attachment_filename)


@app.route('/api/v1/sites/<site>/sensors/<sensor>/<date>/plots/<range_>/<column>')
def extract_plot(site, sensor, date, range_, column):
    """ extracts plot-level data from sensor """

    product = get_sensor_product(site, sensor)

    datepath = check_sensor(site, sensor, date)
    path = os.path.join(datepath, product)
    if not os.path.exists(path):
        raise InvalidUsage('sensor data not available for given date',
                payload={'site':site, 'sensor':sensor, 'date':date})

    boundary = get_plot_boundary(site, date, range_, column)
    plot = clip_plot(path, boundary)
    attachment_filename = plot_attachment_name(site, sensor, date, 
                                               product, range_, column)
    return send_file(plot, as_attachment=True, 
                     attachment_filename=attachment_filename)


@app.route('/api/v1/sites/<site>/sensors')
def list_sensors(site):
    check_site(site)
    return '{}: stereoTop'.format(site)

@app.route('/api/')
def api_active():
    return 'API ACTIVE'

class ReusableForm(Form):
    site = TextField('Site:', validators=[validators.required()])
    sensor = TextField('Sensor:', validators=[validators.required()]) 
    date = TextField('Date:', validators=[validators.required()])


@app.route('/fullfield', methods=['GET', 'POST'])
def fullfield():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        site=request.form['site']
        sensor=request.form['sensor']
        date=request.form['date']

        #if form.validate():
        return redirect(url_for('sensor', site=site, sensor=sensor, date=date))

    return render_template('fullfield.html', form=form, info={"status":""})

@app.route('/plot_service', methods=['GET', 'POST'])
def plot():
    if request.method == 'POST':
        site=request.form['site']
        sensor=request.form['sensor']
        date=request.form['date']
        range_=request.form['range']
        column=request.form['column']

        return redirect(url_for('extract_plot', site=site, sensor=sensor, date=date, range_=range_, column=column))

    return render_template('plot_service.html')
