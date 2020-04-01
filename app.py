from flask import Flask
from waitress import serve
import sys
from os import path

from blocklibs.chain.models import api

app = Flask(__name__)
api.init_app(app)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int("5000"))
    # serve(app,  host='0.0.0.0', port=5000)
