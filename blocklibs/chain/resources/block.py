# import json
# import time
# from http import HTTPStatus as code

# import requests
# from flask import request
# from flask_restplus import Resource, Namespace

# from blockchain.app import api_response, block_chain, api_block
# from blocklibs.chain.controllers.block import Block
# from blocklibs.chain.errors import BlockChainError, HttpErrors, NodeError
# from blocklibs.chain.models.block import (block_resource_fields,
#                                           block_tamper_resource_fields)


# @api_block.route('/add')
# class Blocks(Resource):

#     @api_block.expect(block_resource_fields)
#     def post(self):
#         """
#         Add an external mined block to the chain.
#         """
#         new_block = request.get_json()
#         block = Block(
#             new_block.get("index"),
#             new_block.get("transactions"),
#             new_block.get("timestamp"),
#             new_block.get("previous_hash"),
#             new_block.get("nonce"),
#             new_block.get("merkle_root")
#         )
#         proof = new_block.get("hash")
#         is_block_added = block_chain.add_block(block, proof)

#         if not is_block_added:
#             message = "Block not valid, discarded by the node"
#             return api_response.raise_response(message, code.BAD_REQUEST)

#         message = "Block mined and sent to the nodes"
#         return api_response.raise_response(message, code.CREATED)


# @api_block.route('/tamper')
# class BlockTamper(Resource):

#     @api_block.expect(block_tamper_resource_fields)
#     def post(self):
#         """
#         A new node to simulate a Blockchain tampering.
#         """
#         try:
#             fake_author = request.get_json()["author"]
#             fake_content = request.get_json()["content"]
#             block_index = request.get_json()["block_index"]
#             transaction_index = request.get_json()["transaction_index"]

#             block_chain.chain[block_index].transactions[transaction_index]["author"] = fake_author
#             block_chain.chain[block_index].transactions[transaction_index]["content"] = fake_content

#         except AttributeError:
#             message = "Transaction not found"
#             return api_response.raise_response(message, code.BAD_REQUEST)

#         return f"Transaction {transaction_index} of Block {block_index} Tampered!", code.CREATED
