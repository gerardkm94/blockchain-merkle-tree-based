from blocklibs.crypto.hashing import Hashing
from blocklibs.chain.errors import BlockChainError
from blocklibs.chain.controllers.transaction import Transaction
import json
import time
from http import HTTPStatus as code

from flask import request
from flask_restplus import Resource, Namespace, fields

from blocklibs import api_response
from blocklibs import block_chain

api_transactions = Namespace(
    'Transactions', description='Transactions operations')

transaction_resource_fields = api_transactions.model('Transaction',  {
    'author': fields.String,
    'content': fields.String,
},
)

transaction_validator_resource_fields = api_transactions.model('TransactionValidator',  {
    'transaction_index': fields.Integer,
    'merkle_root': fields.String,
},
)


@api_transactions.route('/unconfirmed')
class Transactions(Resource):

    def get(self):
        """
        Retrieve pending transactions, convert to JSON
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


@api_transactions.route('/validator')
class TransactionValidator(Resource):

    @api_transactions.expect()
    def post(self):
        """
        Receives a Hashed Transaction and its merkle Root and returns a
        its merkle_proof.
        """
        incoming_transaction = request.get_json()
        try:
            transaction_index = incoming_transaction.get("transaction_index")
            merkle_root = incoming_transaction.get("merkle_root")

            transactions = block_chain.get_transactions_by_merkle_root(
                merkle_root)

            if transactions:
                merkle_proof = Hashing.compute_merkle_proof(
                    transactions, transaction_index)

                return api_response.raise_response(json.dumps(merkle_proof), code.CREATED)

        except Exception:
            message = "Input data is not valid, please, check it"
            return api_response.raise_response(message, code.BAD_REQUEST)

        message = "Not transactions found by this merkle root"
        return api_response.raise_response(message, code.NOT_FOUND)


@api_transactions.route('/mine')
class UnconfirmedTransactions(Resource):

    def get(self):
        """
        Mine unconfirmed transactions

        First, call consensus to assure that the chain is in the last version before update
        the block info.
        """
        try:
            is_chain_updated = block_chain.consensus()
            result = block_chain.compute_transactions()
        except BlockChainError:
            message = "No unconfirmed transactions to mine"
            return api_response.raise_response(message, 200)
        else:
            failed_publications = block_chain.publish_new_block()

        if not failed_publications:
            message = f"Block {result} mined. Chain updated: {is_chain_updated}"
        else:
            message = f"""Block {result} mined. Chain updated: {is_chain_updated}.
            Nodes that did not accept the block {json.dumps(failed_publications)}"""

        return api_response.raise_response(message, 200)
