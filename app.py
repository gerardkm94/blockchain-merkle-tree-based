import json
import sys
import time
from http import HTTPStatus as code

import requests
from flask import Flask, request
from flask_restplus import Api, Resource, fields, reqparse
from waitress import serve

from blocklibs.chain.controllers.blockchain import Blockchain
from blocklibs.chain.errors import (ApiResponse, BlockChainError, HttpErrors,
                                    NodeError)
from blocklibs.chain.resources import api

app = Flask(__name__)
api.init_app(app)

# api_transactions = api.namespace(
#     'Transactions', description='Transactions operations')
# api_block = api.namespace(
#     'Block', description='Block Operations')
# api_nodes = api.namespace('Nodes', description='Nodes operations')


# max_request_retry = 3

# Since is development server, we can use app.run for instance, waitress.
# https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/
# It works wen is run with python instead of flask run
if __name__ == '__main__':
    #app.run(debug=False, port=sys.argv[1])
    # Serving with waitress
    serve(app, host='127.0.0.1', port=sys.argv[1])
