import os
from flask import Flask

app = Flask(__name__, template_folder='templates')
app.debug = True
app.config['CLOWDER_URL'] = os.environ['CLOWDER_URL']
app.config['CLOWDER_KEY'] = os.environ['CLOWDER_KEY']

import plot_service.api
import plot_service.api2
import plot_service.views

