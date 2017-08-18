# TerraREF Plot Service

*PROOF OF CONCEPT*

This service provides a RESTful API that takes site, sensor and date
information and returns a list of appropriate files for download.

## API Definition

    # get all sites
    http://hostname/api/v1/sites
    { sites: [ { id: <str>, title: <str>, uri: <url> }, ...  ] }

    # get all sensor associated with a site
    http://hostname/api/v1/sites/:id
    { site: id, 
      collections: [ { id: 'sensors', title: 'Sensors', uri: <url> } ]
    }

    http://hostname/api/v1/sites/:id/sensors
    { site: id, 
      sensors: [ { id: <str>, title: <str>, uri: <url> }, ... ],
    }

    # get all data associated with sensor
    http://hostname/api/v1/sites/:site/sensors/:sensor
    { site: id, sensor: id, 
      collections: [ { id: 'dates', title: 'Dates', uri: <url> }, ... ],
    }

    http://hostname/api/v1/sites/:site/sensors/:sensor/dates
    { site: id, sensor: id, 
      dates: [ { id: <str>, title: YYYY-MM-DD, uri: <url> }, ... ] }
    }

    # from the sensor level various filters can be applied 
    # to limit the list of data files
    ?start=YYYY-MM-DD
    ?start=YYYY-MM-DD&end=YYYY-MM-DD
    ?season=#

    # download the data
    http://hostname/api/v1/sites/:site/sensors/:sensor/dates/:date
    <return file>

    # return a data file clipped to plot boundary
    ?date=YYYY-MM-DD&sitename=<plot name>
    <return clipped file>


## Install
The service is written using Flask and can be installed locally using
WSGI, fcgi, or even using the local development service. But the
recommended approach is to use the docker image and docker-compose file.
