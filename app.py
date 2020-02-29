import json
import time

from flask import Flask, request
from flask_restplus import Resource, Api, reqparse, fields

from blocklibs.chain.blockchain import Blockchain
from blocklibs.chain.node import Node


app = Flask(__name__)
api = Api(app)
block_chain = Blockchain()

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
    @api_transactions.response(201, "Succes")
    def post(self):
        """
        Creates a new transaction
        """
        incoming_transaction = request.get_json()
        required_data = ["author", "content"]

        for mandatory_field in required_data:
            if not incoming_transaction.get(mandatory_field):
                return "Incoming transaction is invalid ", 404

        incoming_transaction["timestamp"] = time.time()
        block_chain.add_new_transaction(incoming_transaction)
        return "Transaction added, pending to validate ", 201


@api_operations.route('/unconfirmed_transactions')
class UnconfirmedTransactions(Resource):

    def get(self):
        """
        Mine unconfirmed transactions
        """
        result = block_chain.compute_transactions
        if not block_chain:
            return "not transactions to mine"
        return "Block #{} mined".format(result)


@api_nodes.route('/node')
class Nodes(Resource):

    def get(self):
        """
        Get the chain of a node
        """
        return block_chain.get_local_chain

    @api_transactions.expect(node_resource_fields)
    @api_transactions.response(201, "Success")
    def post(self):
        """
        Post a new node to the network
        """
        node_address = request.get_json()["node_address"]
        node_name = request.get_son()["node_name"]
        if not node_address:
            return "Nodes aren't specified", 400

        new_node = Node(node_address, node_name)

        block_chain.add_new_node(new_node)

        remote_chain = new_node.get_remote_chain()

        return remote_chain


# Since is development server, we can use app.run for instance, waitress.
# https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/
# It works wen is run with python instead of flask run
# if __name__ == '__main__':
#     app.run(debug=True, port=8000)
