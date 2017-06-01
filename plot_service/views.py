from plot_service import app

@app.route('/')
def index():
    return 'WORKS'

