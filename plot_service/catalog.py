from flask import Flask, send_file, send_from_directory, safe_join, request, render_template
from plot_service import app
import api

@app.route('/catalog/v1/sites')
def catalog_list_sites():
    return render_template('data.html', topic="List of sites", data=api.list_sites())



@app.route('/catalog/v1/sites/<site>/sensors')
def catalog_list_sensors(site):
    topic = "List of sensors in site \"" + site + "\""
    return render_template('data.html', topic=topic, data=api.list_sensors(site))



@app.route('/catalog/v1/sites/<site>/sensors/<sensor>/dates')
def catalog_list_dates(site, sensor):
    topic = "List of dates in site \"" + site + "\", sensor \"" + sensor + "\"" 
    return render_template('data.html', topic=topic, data=api.get_sensor_dates(site, sensor))




















