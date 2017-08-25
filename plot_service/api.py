import os
import requests
import json
import numpy as np
from io import BytesIO
from PIL import Image
from flask import send_file, send_from_directory, safe_join, request
from plot_service import app
from plot_service.exceptions import InvalidUsage
from terrautils.gdal import clip_raster, extract_boundary
from terrautils.betydb import get_site_boundaries
from terrautils.sensors import get_sitename, get_sensor_product
from terrautils.sensors import get_attachment_name, check_sensor
from terrautils.sensors import plot_attachment_name, check_site
from terrautils.sensors import get_file_paths
import terrautils.sensors as Sensors
import json

TERRAREF_BASE = '/projects/arpae/terraref'

@app.route('/api')
def api_active():
    return 'API ACTIVE'


@app.route('/api/v1/sites')
def list_sites():
    """ Get all sites """
    sites = Sensors.get_sites()
    site_map_list = []
    for site in sites:
        site_map = {'_type' : 'str',
                    'id' : site,
                    'title' : site,
                    'href' : '/sites/' + site}
        site_map_list.append(site_map)

    return json.dumps({'resources' : site_map_list})


@app.route('/api/v1/sites/<site>')
def get_site(site):
    """ Get the site's metadata """
    site_map = {'_type' : 'site',
                'title' : site,
                'site' : site,
                'collections' : [{'id' : 'sensors',
                                  'title' : 'Sensors',
                                  'href' : '/sites/' + site + '/sensors'}]}

    return json.dumps(site_map)


@app.route('/api/v1/sites/<site>/sensors')
def list_sensors(site):
    """ Get all sensor associated with a site """
    sensors = Sensors.get_sensors(site)
    sensor_list = []
    for sensor in sensors:
        sensor_map = {'id' : sensor,
                      'title' : sensor,
                      'href' : '/sites/' + site + '/sensors/' + sensor}
        sensor_list.append(sensor_map)

    return json.dumps({'site' : site, 
                       'resources' : sensor_list})


@app.route('/api/v1/sites/<site>/sensors/<sensor>')
def get_sensor_data(site, sensor):
    """ Get all data associated with sensor """
    sensor_collections = [{'id' : 'dates',
                           'title' : 'Dates',
                           'href' : '/sites/' + site + '/sensors/' + sensor}]

    return json.dumps({'site' : site,
                       'sensor' : sensor,
                       'collections' : sensor_collections})


@app.route('/api/v1/sites/<site>/sensors/<sensor>/dates')
def get_sensor_dates(site, sensor):
    # TODO: get all dates and handle query 
    """ Get dates associated with sensor """
    if request.query_string:
        # handle query
        # ?start=start_date
        start = request.args.get('start')
        end = request.args.get('end')
        season = request.args.get('season')

    else:
        # get all dates
        #sensor_dates = Sensors.get_sensor_path('ua-mac', 'Level_1', 'flirIrCamera', '2017-04-27', '2017-04-27__23-12-13-999', '')
    return qs


@app.route('/api/v1/sites/<site>/sensors/<sensor>/dates/<date>')
def download_data(site, sensor, date):
    # TODO: download the data file
    if request.query_string:    # return clipped file
        plot_name = request.args.get('sitename')
    else:   # download the date file
        
    return ""

'''
@app.route('/api/v1/sites/<site>/sensors/<sensor>/<date>')
def sensor(site, sensor, date):
    """Return a downloaded version of the sensor """
    'Sitename = MAC Field Scanner Season 4 Range 10 Column 1'
    # maps from site and sensor to a filename that should be
    # available for every date

    paths = get_file_paths(site, sensor, date)
    product = paths[0].split('/')[-1]

    if all(not os.path.exists(path) for path in paths):
        raise InvalidUsage('sensor data not available for given date',
                           payload={'site': site, 'sensor': sensor,
                                    'date': date})

    sitename = request.args.get('sitename', '')
    if sitename:
        boundary = get_site_boundaries(sitename=sitename)[sitename]
        boundary = extract_boundary(boundary)

        plot = clip_raster(paths[0], boundary)
        print(plot[0].shape)
        plot = np.dstack(plot[0])
        image = Image.fromarray(plot)

        byte_io = BytesIO()
        image.save(byte_io, 'PNG')
        byte_io.seek(0)
        attachment_filename = plot_attachment_name(sitename, sensor, date, product)

        return send_file(byte_io, as_attachment=True,
                         attachment_filename=attachment_filename)

    # encodes site, sensor, date into attachment filename
    attachment_filename = get_attachment_name(site, sensor, date, product)

    return send_file(paths[0], mimetype='image/jpeg')



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
    plot, gt = clip_raster(path, boundary)
    
    #plot = np.reshape(plot, (plot.shape[0]*plot.shape[1],plot.shape[2]))
    plot = np.dstack(plot)
    image = Image.fromarray(plot)

    byte_io = BytesIO()
    image.save(byte_io, 'PNG')
    byte_io.seek(0)
    attachment_filename = plot_attachment_name(sitename, sensor, date, product)
    return send_file(byte_io, as_attachment=True,
                     attachment_filename=attachment_filename)
'''