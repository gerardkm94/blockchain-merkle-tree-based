from flask import Flask
from waitress import serve
import sys
from os import path

from blocklibs.chain.models import api

app = Flask(__name__)
api.init_app(app)

if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=sys.argv[1])
