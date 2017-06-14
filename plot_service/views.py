from flask import render_template, safe_join, request, Flask, redirect, url_for
from flask import send_file, send_from_directory
from wtforms import Form, TextField, TextAreaField, validators
from plot_service import app


TERRAREF_BASE = '/projects/arpae/terraref'


class ReusableForm(Form):

    site = TextField('Site:', validators=[validators.required()])
    sensor = TextField('Sensor:', validators=[validators.required()])
    date = TextField('Date:', validators=[validators.required()])


def get_tif_info(product):

    src = gdal.Open(product)
    ulx, xres, xskew, uly, yskew, yres = src.GetGeoTransform()
    lrx = ulx + (src.RasterXSize * xres)
    lry = uly + (src.RasterYSize * yres)
    extent = [ulx, lry, lrx, uly]
    center = [(ulx+lrx)/2, (uly+lry)/2]

    return (extent, center)


@app.route('/fullfield', methods=['GET', 'POST'])
def fullfield():
    ''' The web interface for getting a fullfield image '''
    form = ReusableForm(request.form)
    if request.method == 'POST':
        site = request.form['site']
        sensor = request.form['sensor']
        date = request.form['date']

        if form.validate():
            return redirect(url_for('mapserver'))

    return render_template('fullfield.html', form=form, info={"status": ""})


@app.route('/mapserver', methods=['POST'])
def mapserver():
    ''' The web interface for showing the fullfield image on a map '''
    # get variables
    mapfile = ('/media/roger/sites/{}/Level_1/{}/{}' +
               '/stereoTop_fullfield_jpeg75.map').format(
                  request.form['site'], request.form['sensor'],
                  request.form['date'])

    # TODO Fix product filename
    product = check_sensor(request.form['site'],
                           request.form['sensor'],
                           request.form['date']) + '/ff.tif'

    extent, center = get_tif_info(product)

    return render_template('mapserver.html', mapfile=mapfile,
                           extent=extent, center=center)


@app.route('/plot_service', methods=['GET', 'POST'])
def plot():
    ''' The web interface for getting a plot image '''
    form = ReusableForm(request.form)
    if request.method == 'POST':
        site = request.form['site']
        sensor = request.form['sensor']
        date = request.form['date']
        range_ = request.form['range']
        column = request.form['column']

        if form.validate():
            url = url_for('extract_plot', site=site, sensor=sensor,
                          date=date, range_=range_, column=column)
            return redirect(url)

    return render_template('plot_service.html', form=form, info={"status": ""})
