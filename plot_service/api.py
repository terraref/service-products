import os
import requests
import json
import numpy as np
from io import BytesIO
from PIL import Image
from flask import send_file, send_from_directory, safe_join, request, render_template
from plot_service import app
from plot_service.exceptions import InvalidUsage
from terrautils.gdal import clip_raster
from terrautils.betydb import get_experiments
#from terrautils.sensors import get_sitename, get_sensor_product
#from terrautils.sensors import get_attachment_name, check_sensor
#from terrautils.sensors import plot_attachment_name, check_site
#from terrautils.sensors import get_file_paths
from terrautils.sensors import Sensors as Sensors_module
import json
import logging
from datetime import datetime

TERRAREF_BASE = '/projects/arpae/terraref/sites'
Sensors = Sensors_module(TERRAREF_BASE, 'ua-mac') # a Sensors instance with a dummy site

####################################################################
def check_site(station):
    """ Checks for valid station given the station name, and return its
    path in the file system.
    """

    if not os.path.exists(TERRAREF_BASE):
        raise InvalidUsage('Could not find data, try setting TERRAREF_BASE environmental variable')

    sitepath = os.path.join(TERRAREF_BASE, station)
    if not os.path.exists(sitepath):
        raise InvalidUsage('unknown site', payload={'site': station})

    return sitepath


def check_sensor(station, sensor, date=None):
    """ Checks for valid sensor with optional date, and return its path
    in the file system.
    """

    sitepath = check_site(station)

    sensorpath = os.path.join(sitepath, 'Level_1', sensor)
    if not os.path.exists(sensorpath):
        raise InvalidUsage('unknown sensor',
                           payload={'site': station, 'sensor': sensor})

    if not date:
        return sensorpath

    datepath = os.path.join(sensorpath, date)
    logging.info("datepath = {}".format(datepath))

    if not os.path.exists(datepath):
        raise InvalidUsage('sensor data not available for given date',
                           payload={'site': station, 'sensor': sensor,
                                    'date': date})

    return datepath


def list_sensor_dates(station, sensor):
    """ Return a list of all dates of the sensor """
    sensor_path = check_sensor(station, sensor)
    return os.listdir(sensor_path)

def get_experiment_dates(experiment_name):
    """ Get the given experiment's starting date and end date """
    experiments = get_experiments()
    for e in experiments:
        if experiment_name == e['name']:
            return [e['start_date'], e['end_date']]
    return None 
#TODO: functions ABOVE need to move to terrautils in the future

@app.route('/api')
def api_active():
    return 'API ACTIVE'


@app.route('/api/v1/sites')
def api_list_sites():
    return json.dumps(list_sites()) 


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
    data = {'resources' : site_map_list}
    topic = "List of sites"
    return data


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
def api_list_sensors(site):
    return json.dumps(list_sensors(site))


def list_sensors(site):
    """ Get all sensor associated with a site """
    sensors = Sensors.get_sensors(site)
    sensor_list = []
    for sensor in sensors:
        sensor_map = {'id' : sensor,
                      'title' : sensor,
                      'href' : '/sites/' + site + '/sensors/' + sensor}
        sensor_list.append(sensor_map)

    data = {'site' : site, 
            'resources' : sensor_list}
    
    return data


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
def api_get_sensor_dates(site, sensor):
    return json.dumps(get_sensor_dates(site, sensor))


def get_sensor_dates(site, sensor):
    """ Get dates associated with sensor """
    resources = []
    dates = list_sensor_dates(site, sensor)
    print site, sensor
    if dates:
        dates = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
        dates.sort()

        if request.args:
             # handle query
             start = request.args.get('start')
             end = request.args.get('end')
             experiment = request.args.get('experiment')

             ordered_dates = []
             start_date = dates[0]        # default query start date
             end_date = dates[-1]         # default query end date
             
             if start:
                 start_date = datetime.strptime(start, '%Y-%m-%d').date()
             if end:
                 end_date = datetime.strptime(end, '%Y-%m-%d').date()
             if experiment:
                experiment_dates = get_experiment_dates(experiment)
                if experiment_dates == None:
                   dates = []
                else:
                   start_date = datetime.strptime(experiment_dates[0], '%Y-%m-%d').date()
                   end_date = datetime.strptime(experiment_dates[1], '%Y-%m-%d').date()
             
             for date in dates:
                 if date >= start_date and date <= end_date:
                     ordered_dates.append(date)
             
             dates = ordered_dates

        dates = [date.strftime('%Y-%m-%d') for date in dates]

    for date in dates:
        date_map = {'id' : date,
                    'title' : date,
                    'href' : '/sites/' + site + '/sensors/' + sensor + '/dates/' + date}
     
        resources.append(date_map)
            
    data = {'site' : site,
            'sensor' : sensor,
            'resources' : resources}

    return data


 
@app.route('/api/v1/sites/<site>/sensors/<sensor>/dates/<date>')
def download_data(site, sensor, date):
    # TODO: download the data file
    if request.args:    # return clipped file
        #sitename = request.args.get('sitename')
        #mode = request.args.get('mode')
        sitename = "Ashland Bottoms KSU 2016 Season Range 10 Pass 7"
        path = "/projects/arpae/terraref/sites/ua-mac/Level_1/fullfield/2017-05-29/"
        raster_path = path + "flirIrCamera_fullfield.tif"#"fullfield_L1_ua-mac_2017-05-29_rgb.tif"
        features_path = path + "index_2017-05-29.shp"
        #boundary = get_sitename_boundary(sitename)
        plot, gt = clip_raster(raster_path, features_path)
        plot = np.dstack(plot)
        image = Image.fromarray(plot)
 
        byte_io = BytesIO()
        image.save(byte_io, 'PNG')
        byte_io.seek(0)
        attachment_filename = "asdf" #plot_attachment_name(sitename, sensor, date, product)
        return send_file(byte_io, as_attachment=True,
                         attachment_filename=attachment_filename)


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
