import json
import time

from flask import Flask, request
from flask_restplus import Resource, Api, reqparse, fields

from blocklibs.chain.blockchain import Blockchain

app = Flask(__name__)
api = Api(app)
bc = Blockchain()

api_transactions = api.namespace(
    'Transactions', description='Transactions operations')
api_operations = api.namespace(
    'Operations', description='Computational operations')
api_nodes = api.namespace('Nodes', description='Nodes operations')

# Data Schemas definition
resource_fields = api.model('Transaction',  {
    'author': fields.String,
    'content': fields.String,
},
)


@api_transactions.route('/transactions')
class Transactions(Resource):

    def get(self):
        """
        Retrieve pending transactions
        """
        return json.dumps(bc.unconfirmed_transactions)

    @api_transactions.expect(resource_fields)
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
        bc.add_new_transaction(incoming_transaction)
        return "Transaction added, pending to validate ", 201


@api_operations.route('/unconfirmed_transactions')
class UnconfirmedTransactions(Resource):

    def get(self):
        """
        Mine unconfirmed transactions
        """
        result = bc.compute_transactions
        if not bc:
            return "not transactions to mine"
        return "Block #{} mined".format(result)


@api_nodes.route('/node')
class Node(Resource):

    def get(self):
        """
        Get a node
        """
        node_data = []
        for block in bc.chain:
            node_data.append(block.get_block)
        return json.dumps({"length": len(node_data),
                           "chain": node_data})

    def post(self):
        """
        Post a new node to the network
        """
        nodes = request.get_json()
        if not nodes:
            return "Nodes aren't valid", 400
        for node in nodes:
            bc.peers.add(node)

        return "Node added, welcome!", 201


# Since is development server, we can use app.run for instance, waitress.
# https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/
# It works wen is run with python instead of flask run
if __name__ == '__main__':
    app.run(debug=True, port=8000)
