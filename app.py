import json
import time
import requests
from http import HTTPStatus as code

from flask import Flask, request
from flask_restplus import Api, Resource, fields, reqparse
from requests.exceptions import ConnectionError

from blocklibs.chain.blockchain import Blockchain
from blocklibs.chain.errors import ApiResponse, BlockChainError, HttpErrors, NodeError
from blocklibs.chain.node import Node
from blocklibs.chain.transaction import Transaction
from blocklibs.chain.utils import Utils

app = Flask(__name__)
api = Api(app)
block_chain = Blockchain()
api_response = ApiResponse()

max_request_retry = 3

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
        Retrieve pending transactions, convert to JSON_Serializable
        and return the value
        """
        unconfirmed_transactions = []
        # pylint: disable=not-an-iterable
        for unconfirmed in block_chain.unconfirmed_transactions:
            unconfirmed_transactions.append(unconfirmed.transaction)

        return unconfirmed_transactions

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
        block_chain.unconfirmed_transactions = new_transaction

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
        return block_chain.chain_local_info, 200


@api_nodes.route('/register_node')
class Nodes(Resource):

    @api_nodes.expect(node_resource_fields)
    def post(self):
        """
        A new node registers in to the network, and local chain info is returned to be synced
        in foreign nodes.
        """
        try:
            new_node = Node.build_node_from_request(request)
            block_chain.nodes = new_node

        except HttpErrors:
            message = "Can't add the node to the Chain. Invalid data"
            return api_response.raise_response(message, code.REQUEST_TIMEOUT)
        except NodeError:
            message = "Node is already registered"
            return api_response.raise_response(message, code.FORBIDDEN)

        return block_chain.chain_local_info, code.CREATED


@api_nodes.route('/sync_node')
class RegisterNode(Resource):
    @api_nodes.expect(node_resource_fields)
    def post(self):
        """
        Register a new node to the network
        """

        try:
            post_data = {
                'node_address': request.host_url, 'node_name': request.json.get('node_name')
            }
            headers = {'Content-Type': "application/json"}

            for _ in range(0, max_request_retry):

                response = requests.post(
                    f"{request.json.get('node_address')}/Nodes/register_node",
                    data=json.dumps(post_data),
                    headers=headers
                )

                if response.status_code == code.CREATED:
                    break

                elif response.status_code == code.FORBIDDEN:
                    message = response.reason
                    return api_response.raise_response(message, code.FORBIDDEN)

        except HttpErrors:
            message = "Can't request to the node"
            return api_response.raise_response(message, code.BAD_REQUEST)

        if response.status_code == code.CREATED:

            remote_node_info = response.json()

            try:
                received_block_chain = block_chain.chain_builder(
                    remote_node_info.get('chain')
                )

            except BlockChainError as bc_error:
                return api_response.raise_response(str(bc_error), code.METHOD_NOT_ALLOWED)

            else:
                block_chain.chain = received_block_chain
                block_chain.nodes_update = remote_node_info.get('nodes')
                return api_response.raise_response("Registration successful", 201)

        else:
            return api_response.raise_response("Can't sync to remote node", response.status_code)


# Since is development server, we can use app.run for instance, waitress.
# https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/
# It works wen is run with python instead of flask run
if __name__ == '__main__':
    app.run(debug=True, port=8000)
