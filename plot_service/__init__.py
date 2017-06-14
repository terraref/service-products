from flask import Flask

app = Flask(__name__, template_folder='templates')
app.debug = True

import plot_service.api
import plot_service.views

