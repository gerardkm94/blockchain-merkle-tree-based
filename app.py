from flask import request
from blocklibs.chain.blockchain import Blockchain
from flask import Flask
import time
import json

app = Flask(__name__)
bc = Blockchain()


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    incoming_transaction = request.get_json()
    required_data = ["author", "content"]

    for mandatory_field in required_data:
        if not incoming_transaction.get(mandatory_field):
            return "Incoming transaction is invalid", 404

    incoming_transaction["timestamp"] = time.time()
    bc.add_new_transaction(incoming_transaction)

    return "Transaction added, pending to validate", 201

# equivalent to chain
@app.route('/node', methods=['GET'])
def get_node():
    node_data = []
    for block in bc.chain:
        node_data.append(block.get_block)
    return json.dumps({"length": len(node_data),
                       "chain": node_data})


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = bc.compute_transactions
    if not bc:
        return "not transactions to mine"
    return "Block #{} mined".format(result)


@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(bc.unconfirmed_transactions)


# Since is development server, we can use app.run for instance, waitress.
# https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/
# It works wen is run with python instead of flask run
if __name__ == '__main__':
    app.run(debug=True, port=8000)


