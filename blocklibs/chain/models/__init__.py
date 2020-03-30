from blocklibs.chain.resources.transaction import api_transactions
from blocklibs.chain.resources.node import api_nodes
from blocklibs.chain.resources.block import api_block

from flask_restplus import Api, Resource, fields, reqparse

api = Api()

api.add_namespace(api_transactions)
api.add_namespace(api_nodes)
api.add_namespace(api_block)
