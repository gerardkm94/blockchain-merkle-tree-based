# import json
# import time
# import requests
# from http import HTTPStatus as code

# from flask import request
# from flask_restplus import Resource, Namespace

# from blockchain.app import block_chain, api_response, api_nodes
# from blocklibs.chain.errors import NodeError, HttpErrors, BlockChainError
# from blocklibs.chain.models.node import (
#     node_sync_resource_fields, node_name_resource_fields, node_register_resource_fields)
# from blocklibs.chain.controllers.node import Node


# @api_nodes.route('/chain')
# class Chain(Resource):

#     def get(self):
#         """
#         Get the chain of the current node
#         """
#         try:
#             return block_chain.chain_local_info, 200

#         except NodeError as name_error:
#             return api_response.raise_response(str(name_error), 500)


# @api_nodes.route('/trustable')
# class Trustable(Resource):

#     def get(self):
#         """
#         Get the current status of the Node (Trustable or not)
#         """
#         is_trustable = block_chain.is_trustable()

#         if isinstance(is_trustable, str):
#             return is_trustable
#         elif is_trustable:
#             return "Your chain is okay! You're good to go!", 200
#         else:
#             return "Your chain has been tampered :(, please, re-sync to a trusted node!", 200


# @api_nodes.route('/vote')
# class Voting(Resource):
#     def get(self):
#         """
#         Vote the chain as not trustable
#         """
#         block_chain.votes = 1
#         return "Voted as not trustable!", 200


# @api_nodes.route('/set_name')
# class NodeName(Resource):

#     @api_nodes.expect(node_name_resource_fields)
#     def post(self):
#         """
#         Add a name to the current node instance
#         """
#         try:
#             block_chain.self_node_identifier = Node(
#                 request.host_url.rstrip('/'), request.json.get('node_name')
#             )

#         except:
#             message = "Can't name the node like that, please, choose another name"
#             return api_response.raise_response(message, 500)

#         return f"Name Set to {request.json.get('node_name')}", 200


# @api_nodes.route('/register_node')
# class Nodes(Resource):

#     @api_nodes.expect(node_register_resource_fields)
#     def post(self):
#         """
#         A new node registers in to the network, and local chain info is returned to be synced
#         in foreign nodes.
#         """
#         try:
#             new_node = Node.build_node_from_request(request)
#             block_chain.nodes = new_node

#         except HttpErrors:
#             message = "Can't add the node to the Chain. Invalid data"
#             return api_response.raise_response(message, code.REQUEST_TIMEOUT)
#         except NodeError:
#             message = "Node is already registered"
#             return api_response.raise_response(message, code.FORBIDDEN)

#         return block_chain.chain_local_info, code.CREATED


# @api_nodes.route('/sync_node')
# class RegisterNode(Resource):
#     @api_nodes.expect(node_sync_resource_fields)
#     def post(self):
#         """
#         Register a new node to the network
#         """

#         try:
#             node_address = request.json.get('node_address')
#             response = block_chain.register_node(node_address)

#         except HttpErrors:
#             message = "Can't request to the node"
#             return api_response.raise_response(message, code.BAD_REQUEST)

#         except AttributeError:
#             message = "Please, set a name for your node"
#             return api_response.raise_response(message, code.NOT_FOUND)

#         if response.status_code == code.CREATED:

#             remote_node_info = response.json()

#             try:
#                 received_block_chain = block_chain.chain_builder(
#                     remote_node_info
#                 )

#             except BlockChainError as bc_error:
#                 requests.get(f"{node_address}/Nodes/vote")
#                 return api_response.raise_response(str(bc_error), code.METHOD_NOT_ALLOWED)

#             else:
#                 # Adding chain
#                 block_chain.chain = received_block_chain.chain

#                 # Adding received nodes, and deleting own node
#                 received_nodes = Node.serialize_nodes(
#                     remote_node_info.get('nodes'),
#                     block_chain.self_node_identifier.get_node_info())
#                 block_chain.nodes_update = received_nodes

#                 for node in received_nodes:
#                     # Register mi node in all received nodes
#                     block_chain.register_node(node.node_address)

#                 # Adding remote node
#                 block_chain.nodes_update = Node.serialize_nodes(
#                     [remote_node_info.get('node_identifier')],
#                     block_chain.self_node_identifier.get_node_info())

#                 return api_response.raise_response("Registration successful", 201)

#         else:
#             return api_response.raise_response("Can't sync to remote node", response.status_code)
