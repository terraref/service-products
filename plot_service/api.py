import os
import requests
import json
import numpy as np
from io import BytesIO
from PIL import Image
from flask import send_file, send_from_directory, safe_join, request
from plot_service import app
from plot_service.exceptions import InvalidUsage
from plot_service.clip_plot import clip_raster

TERRAREF_BASE = '/projects/arpae/terraref'


def get_sitename(site, date, range_, column):

    sitename = 'MAC Field Scanner Season 4 Range {} Column {}'.\
              format(range_, column)
    return sitename


def get_sitename_boundary(sitename):

    api = 'lxPgymT3ULP2Y13qU02Zp7XjBMUPRICspc7cYbQX'

    url = ('https://terraref.ncsa.illinois.edu/bety/sites.json' +
           '?key={}&sitename={}').format(api, sitename)

    r = requests.get(url, auth=('xawjx1996928', 'xawjx88932489'))
    data = r.json()[0]['site']['geometry'][10:-2]
    coords = data.split(',')

    vertices = []
    for coord in coords:
        x_and_y = coord.split()[:2]
        x_and_y[0] = float(x_and_y[0])
        x_and_y[1] = float(x_and_y[1])
        vertices.append(x_and_y)

    boundary = {
        'type': 'Polygon',
        'coordinates': [vertices]
    }

    return json.dumps(boundary)


def check_site(site):
    ''' check for valid site given the site name '''
    terraref = os.environ.get('TERRAREF_BASE', TERRAREF_BASE)
    if not os.path.exists(terraref):
        raise InvalidUsage('Could not find TerraREF data, try setting '
                           'TERRAREF_BASE environmental variable')

    sitepath = safe_join(terraref, 'sites', site)
    if not os.path.exists(sitepath):
        raise InvalidUsage('unknown site', payload={'site': site})

    return sitepath


def check_sensor(site, sensor, date=None):
    """check for valid sensor with optional date """

    sitepath = check_site(site)

    sensorpath = safe_join(sitepath, 'Level_1', sensor)
    if not os.path.exists(sensorpath):
        raise InvalidUsage('unknown sensor',
                           payload={'site': site, 'sensor': sensor})

    if not date:
        return sensorpath

    datepath = safe_join(sensorpath, date)
    print("datepath = {}".format(datepath))
    if not os.path.exists(datepath):
        raise InvalidUsage('sensor data not available for given date',
                           payload={'site': site, 'sensor': sensor,
                                    'date': date})

    return datepath


def get_sensor_product(site, sensor):
    """Returns the downloadable product for each site-sensor pair"""

    # TODO do something much more intelligent
    return "ff.tif"


def get_attachment_name(site, sensor, date, product):
    """Encodes site, sensor, and date to create a unqiue attachment name"""

    root, ext = os.path.splitext(product)
    return "{}-{}-{}.{}".format(site, sensor, date, ext)


def plot_attachment_name(sitename, sensor, date, product):
    """Encodes sitename, sensor, and date to create a unqiue attachment name"""

    root, ext = os.path.splitext(product)
    return "{}-{}-{}.{}".format(sitename, sensor, date, ext) 


@app.route('/api/v1/sites/<site>/sensors/<sensor>/<date>')
def sensor(site, sensor, date):
    """Return a downloaded version of the sensor """
    'Sitename = MAC Field Scanner Season 4 Range 10 Column 1'
    # maps from site and sensor to a filename that should be
    # available for every date
    product = get_sensor_product(site, sensor)

    datepath = check_sensor(site, sensor, date)
    path = os.path.join(datepath, product)
    if not os.path.exists(path):
        raise InvalidUsage('sensor data not available for given date',
                           payload={'site': site, 'sensor': sensor,
                                    'date': date})

    sitename = request.args.get('sitename', '')
    if sitename:
        s = sitename.split('Range ')
        coord = s[1].split(' Column ')
        range_ = int(coord[0])
        column = int(coord[1])
        boundary = get_sitename_boundary(sitename)
        plot = clip_raster(path, boundary)

        plot = np.dstack(plot)
        image = Image.fromarray(plot)

        byte_io = BytesIO()
        image.save(byte_io, 'PNG')
        byte_io.seek(0)
        attachment_filename = plot_attachment_name(sitename, sensor, date, product)

        return send_file(byte_io, as_attachment=True,
                         attachment_filename=attachment_filename)

    # encodes site, sensor, date into attachment filename
    attachment_filename = get_attachment_name(site, sensor, date, product)

    return send_file(safe_join(datepath, 'ff.jpeg'), mimetype='image/jpeg')


@app.route('/api/v1/sites/<site>/sensors/<sensor>/<date>' +
           '/plots/<range_>/<column>')
def extract_plot(site, sensor, date, range_, column):
    """ extracts plot-level data from sensor """
    product = get_sensor_product(site, sensor)

    datepath = check_sensor(site, sensor, date)
    path = os.path.join(datepath, product)
    if not os.path.exists(path):
        raise InvalidUsage('sensor data not available for given date',
                           payload={'site': site, 'sensor': sensor,
                                    'date': date})

    sitename = get_sitename(site, date, range_, column)
    boundary = get_sitename_boundary(sitename)
    plot = clip_raster(path, boundary)
    
    #plot = np.reshape(plot, (plot.shape[0]*plot.shape[1],plot.shape[2]))
    plot = np.dstack(plot)
    image = Image.fromarray(plot)

    byte_io = BytesIO()
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    attachment_filename = plot_attachment_name(sitename, sensor, date, product)
    return send_file(byte_io, as_attachment=True,
                     attachment_filename=attachment_filename)


@app.route('/api/v1/sites/<site>/sensors')
def list_sensors(site):
    ''' List all the sensors in the given site '''
    check_site(site)
    return '{}: stereoTop'.format(site)


@app.route('/api/')
def api_active():
    return 'API ACTIVE'
