from blocklibs.chain.resources.transaction import api_transactions as n1
from flask_restplus import Api, Resource, fields, reqparse

# from blocklibs.chain.resources.node import api_nodes
# from blocklibs.chain.resources.block import api_block

api = Api()

api.add_namespace(n1)
api.namespace(
    'Transactions', description='Transactions operations')
