from flask import Flask
app = Flask(__name__, template_folder='templates')

import plot_service.api
import plot_service.views 
