# TerraREF Plot Service

*PROOF OF CONCEPT*

This service provides a RESTful API that takes date and plot id as input
and returns plot level data.

## API Definition
GET http://hostname/api/v1/sensors
GET http://hostname/api/v1/sensors/<sensor>/plots/<date>/<range>/<pass>

GET http://hostname/api/v1/plots/<date>
GET http://hostname/api/v1/plots/<date>/<range>/<pass>

## Install
The service is written using Flask and can be installed locally using
WSGI, fcgi, or even using the local development service. But the
recommended approach is to use the docker image and docker-compose file.

