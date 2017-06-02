# TerraREF Plot Service

*PROOF OF CONCEPT*

This service provides a RESTful API that takes date and plot id as input
and returns plot level data.

## API Definition
GET http://hostname/api/v1/sites/:site/sensors -- list all available sensors

GET http://hostname/api/v1/sites/:site/sensors/:sensor/:date -- downloadable sensor product

GET http://hostname/api/v1/sites/:site/sensors/:sensor/:date/plots/:range/:column -- extract plot data from sensor product

## Install
The service is written using Flask and can be installed locally using
WSGI, fcgi, or even using the local development service. But the
recommended approach is to use the docker image and docker-compose file.
