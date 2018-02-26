# TERRA REF Product Service

This service provides a RESTful API that takes sensor, plot and date
information and returns a list of appropriate files for download.

_Use version 2 of the API, version 1 support will disappear soon_

## API Definition

The API consists of two collections, files and sensors. File collections 
are set of file paths associated with a sensor. The API allows files to 
be filtered by plot boundary and time period. Users are able use the 
file path to locate specific data files from the workbench or Globus.

The sensor collection roughly corresponds to set of raw data files 
(level 0) collected at a remote station or secondary data files 
(level 1) processed by the TERRA-REF pipeline. The sensor names are 
generated dynamically from an internal database and not all sensors 
have data associated with them.

## Examples

The following examples demonstrate using the API from curl and provides
sample output. This service provides a high-level mechanism to query
the Clowder API using names (human-readable strings) rather than ids. 

Querying the files collection requires two parameters, sensor_name and 
sitename. The sensor_name should be one of the names returned from
the sensor colletion (see below). The sitename is the name of a plot 
as defined in betydb.

Note: the following curl command pass the parameters using the
--data-urlencode option because of the spaces. When --data options are
used curl default to using the http POST method, the -G options sets
it back to GET.

```
> curl --data-urlencode "sensor_name=Thermal IR GeoTIFFs Datasets" --data-urlencode "sitename=MAC Field Scanner Season 1 Field Plot 111 W" -G https://sensorquery.workbench.terraref.org/api/v2/files

[
  {
    "contentType": "image/png",
    "date-created": "Fri Nov 03 11:44:56 CDT 2017",
    "filename": "ir_geotiff_L1_ua-mac_2016-05-09__12-06-40-529.png",
    "filepath": "/home/clowder/sites/ua-mac/Level_1/ir_geotiff/2016-05-09/2016-05-09__12-06-40-529/ir_geotiff_L1_ua-mac_2016-05-09__12-06-40-529.png",
    "id": "59fc9d084f0c3383c73d041d",
    "size": "370942"
  },
  {
    "contentType": "image/tiff",
    "date-created": "Fri Nov 03 11:44:57 CDT 2017",
    "filename": "ir_geotiff_L1_ua-mac_2016-05-09__12-06-40-529.tif",
    "filepath": "/home/clowder/sites/ua-mac/Level_1/ir_geotiff/2016-05-09/2016-05-09__12-06-40-529/ir_geotiff_L1_ua-mac_2016-05-09__12-06-40-529.tif",
    "id": "59fc9d094f0c3383c73d0437",
    "size": "1231298"
  },

...
]
```

The request can be further refined with the use of the since and until
parameters to limit the time range of the query.

> curl --data-urlencode "sensor_name=Thermal IR GeoTIFFs Datasets" --data-urlencode "sitename=MAC Field Scanner Season 1 Field Plot 111 W" --data "since=2016-05-09" --data "until=2016-05-31" -G https://sensorquery.workbench.terraref.org/api/v2/files

Generally speaking the sensor names should be well known to the user
from the document. But a list of all sensors can be retrieved from the
API as shown below.

```
> curl https://sensorquery.workbench.terraref.org/api/v2/sensors
[
  {
    "created": "2017-09-07T18:46:14Z",
    "end_time": null,
    "geometry": {
      "coordinates": [
        33.075576,
        -68.025696,
        361
      ],
      "type": "Point"
    },
    "id": 3211,
    "name": "Weather Observations",
    "params": null,
    "properties": {},
    "sensor_id": "438",
    "start_time": null,
    "type": "Feature"
  },
  {
    "created": "2018-02-26T09:41:52Z",
    "created": "2017-11-06T05:54:46Z",
    "end_time": null,
    "geometry": {
      "coordinates": [
        [
          [ -111.974835225614, 33.0757144472862, 353 ],
          [ -111.974818834914, 33.0757144550186, 353 ],
          [ -111.97481881276, 33.0756812187252, 353 ],
          [ -111.974835203454, 33.075681210993, 353 ],
          [ -111.974835225614, 33.0757144472862, 353 ]
        ]
      ],
      "type": "Polygon"
    },
    "id": 7245,
    "name": "Thermal IR GeoTIFFs Datasets (1560)",
    "params": null,
    "properties": {},
    "sensor_id": "1560",
    "start_time": null,
    "type": "Feature"
  },
...
]
```

More conveniently, setting the parameter _names_ to 'true' returns a list
of sensors names currently supported with TERRA-REF. Note that not all of
these sensor names will have a file products associated with them.

```
> curl https://sensorquery.workbench.terraref.org/api/v2/sensors?names=true
[
"IR Surface Temperature",
"Thermal IR GeoTIFFs Datasets",
"flirIrCamera Datasets",
"Laser Scanner 3D LAS Datasets",
"(EL) sensor_weather_station",
"Irrigation Observations",
"Canopy Cover",
"Energy Farm Observations SE",
"(EL) sensor_par",
"scanner3DTop Datasets",
"Weather Observations",
"Energy Farm Observations NE",
"RGB GeoTIFFs Datasets",
"(EL) sensor_co2",
"stereoTop Datasets",
"Energy Farm Observations CEN"
]

