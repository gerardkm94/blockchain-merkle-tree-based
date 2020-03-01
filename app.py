import json
import time
from http import HTTPStatus as code

from flask import Flask, request
from flask_restplus import Api, Resource, fields, reqparse
from requests.exceptions import ConnectionError

from blocklibs.chain.blockchain import Blockchain
from blocklibs.chain.errors import ApiResponse, BlockChainError
from blocklibs.chain.node import Node
from blocklibs.chain.transaction import Transaction

app = Flask(__name__)
api = Api(app)
block_chain = Blockchain()
api_response = ApiResponse()

api_transactions = api.namespace(
    'Transactions', description='Transactions operations')
api_operations = api.namespace(
    'Operations', description='Computational operations')
api_nodes = api.namespace('Nodes', description='Nodes operations')

# Data Schemas definition Move to its package
transaction_resource_fields = api.model('Transaction',  {
    'author': fields.String,
    'content': fields.String,
},
)

node_resource_fields = api.model('Node',  {
    'node_address': fields.Url,
    'node_name': fields.String,
},
)


@api_transactions.route('/transactions')
class Transactions(Resource):

    def get(self):
        """
        Retrieve pending transactions
        """
        return json.dumps(block_chain.unconfirmed_transactions)

    @api_transactions.expect(transaction_resource_fields)
    def post(self):
        """
        Creates a new transaction
        """
        incoming_transaction = request.get_json()
        try:
            author = incoming_transaction.get("author")
            content = incoming_transaction.get("content")
        except Exception:
            message = "Input data is not valid, please, check it"
            return api_response.raise_response(message, code.BAD_REQUEST)

        new_transaction = Transaction(author, content, time.time())
        block_chain.add_new_transaction(new_transaction)

        message = "Transaction added, pending to validate "
        return api_response.raise_response(message, code.CREATED)


@api_operations.route('/unconfirmed_transactions')
class UnconfirmedTransactions(Resource):

    def get(self):
        """
        Mine unconfirmed transactions
        """
        try:
            result = block_chain.compute_transactions()
        except BlockChainError:
            message = "No unconfirmed transactions to mine"
            return api_response.raise_response(message, 200)

        message = "Block #{} mined".format(result)
        return api_response.raise_response(message, 200)


@api_nodes.route('/chain')
class Chain(Resource):
    def get(self):
        """
        Get the chain of the current node
        """
        return block_chain.get_local_chain, 200


@api_nodes.route('/node')
class Nodes(Resource):

    @api_transactions.expect(node_resource_fields)
    def post(self):
        """
        Post a new node to the network
        """
        try:
            node_address = request.get_json()["node_address"]
            node_name = request.get_json()["node_name"]
        except:
            message = "No node_address or name was provided"
            return api_response.raise_response(message, code.BAD_REQUEST)

        new_node = Node(node_address, node_name)
        block_chain.add_new_node(node=new_node)

        try:
            remote_chain = new_node.get_remote_chain()
        except ConnectionError:
            message = "Can't get remote chain"
            return api_response.raise_response(message, code.REQUEST_TIMEOUT)

        return remote_chain, 200


# Since is development server, we can use app.run for instance, waitress.
# https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/
# It works wen is run with python instead of flask run
if __name__ == '__main__':
    app.run(debug=True, port=8000)
