
# https://github.com/terraref/tutorials/blob/geostreams-guide/sensors/06-list-datasets-by-plot.md
import os
import requests
from flask import request, jsonify
from terrautils.geostreams import get_sensor_by_name
from plot_service import app

import logging
log = logging.getLogger(__name__)

HOST = app.config['CLOWDER_URL']
KEY = app.config['CLOWDER_KEY']

PLOTS = os.path.join(HOST, 'api/geostreams/sensors')
STREAMS = os.path.join(HOST, 'api/geostreams/streams')
DATAPOINTS = os.path.join(HOST, 'api/geostreams/datapoints')
DATASETS = os.path.join(HOST, 'api/datasets')


def get_plot_id(sitename):
    """return sensor ID from geostreams based on sitename"""

    sensor = get_sensor_by_name(None, HOST, KEY, sitename)
    return sensor['id'] if sensor else None


# TODO this should be from the pyclowder package
def get_sensor_list():
    """return a list of all sensors"""

    r = requests.get(STREAMS)
    r.raise_for_status()
    return r.json()


def unique_sensor_names(sensors=None):
    """returns a list of unique sensor names"""

    if not sensors:
        sensors = get_sensor_list()

    rsp = set()
    for s in sensors:
        if s['name'].endswith(')'):
            rsp.add(s['name'].split('(')[0].strip())
        else:
            rsp.add(s['name'])

    return list(rsp)


@app.route('/api/v2/plots')
def api2_plot_collection():

    sitename = request.args.get('sitename', '')
    if sitename:
        params = { 'sensor_name': sitename }
    else:
        params = {}
    
    r = requests.get(PLOTS, params=params)
    r.raise_for_status()
    return jsonify(r.json())


@app.route('/api/v2/plots/<int:plot>')
def api2_plot(plot):

    params = { 'id': plot }
    r = requests.get(PLOTS, params=params)
    r.raise_for_status()
    return jsonify(r.json())


@app.route('/api/v2/sensors')
def api2_sensor_collection():
    
    r = requests.get(STREAMS)
    r.raise_for_status()

    # if sitename is provided return streams that end with sensor id
    if request.args.get('sitename', ''):
        pid = '({})'.format(get_plot_id(request.args.get('sitename')))
        rsp = [s for s in r.json() if s['name'].endswith(pid)]
        return jsonify(rsp)

    # otherwise turn unique portion of stream names as list
    if request.args.get('names', 'false') == 'true':
        return jsonify(unique_sensor_names(r.json()))

    # return all streams
    return jsonify(r.json())


def get_datapoints(sensor):
    # TODO remap since/until parameters to start/end?
    params = dict(request.args)
    params['stream_id'] = sensor

    r = requests.get(DATAPOINTS, params=params)
    r.raise_for_status()
    return r


@app.route('/api/v2/sensors/<int:sensor>')
def api2_sensor(sensor):

    return jsonify(get_datapoints(sensor))


@app.route('/api/v2/sensors/<int:sensor>/files')
def api2_sensor_files(sensor):

    datapoints = get_datapoints(sensor).json()

    # TODO unpack the datapoints to datasets and get the files


def get_sensor(sensor, sitename=''):

    if not sensor:
        raise RuntimeError('sensor_name parameter required')

    # append the sitename id if given
    if sitename:
        pid = get_plot_id(request.args.get('sitename'))
        if not sensor.endswith(')'):
            sensor += ' ({})'.format(pid)
    
    r = requests.get(STREAMS, params={'stream_name': sensor})
    r.raise_for_status()
    return r    


def get_files(dataset):
    """returns all files in a dataset"""

    dataset_id = dataset.split('/')[-1]
    if dataset_id == 'files':
        dataset_id = dataset.split('/')[-2]
    dataset = '/'.join((DATASETS, dataset_id, 'files')) 

    r = requests.get(dataset, params={'key': KEY})
    r.raise_for_status()
    return r.json()


def file_listing(sensor, sitename, since='', until=''):

    r = get_sensor(sensor, sitename)
    stream_id = r.json()[0]['id']
    log.debug('stream_id = %s', stream_id)

    params = { 'stream_id': stream_id }
    if since:
        params['since'] = since
    if until:
        params['until'] = until

    r = requests.get(DATAPOINTS, params=params)
    r.raise_for_status()
    datasets = [ds['properties']['source_dataset'] for ds in r.json()]

    files = []
    for ds in datasets:
        flist = get_files(ds)
        if flist:
            files.extend(flist)
    return files
    
    
# http://production.roger.ncsa.illinois.edu:8000/api/v2/files?sensor_name=Thermal%20IR%20GeoTIFFs%20Datasets&sitename=MAC%20Field%20Scanner%20Season%201%20Field%20Plot%20101%20W
@app.route('/api/v2/files')
def api2_file_collection():

    flist = file_listing(request.args.get('sensor_name', ''),
                         request.args.get('sitename'),
                         since=request.args.get('since', ''),
                         until=request.args.get('until', ''))
    return jsonify(flist)
    
