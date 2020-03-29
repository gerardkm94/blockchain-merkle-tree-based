

import datetime
import json
from http import HTTPStatus as code

import requests

from blocklibs.chain.errors import HttpErrors, NodeError, SerializeNodeError


class Node():

    def __init__(self, node_address, node_name):
        self._node_address = node_address
        self._node_name = node_name

    def __eq__(self, other):
        return (self.get_node_info() == other.get_node_info())

    def __hash__(self):
        return hash(self._node_address + self._node_name)

    def get_node_info(self):
        node = json.dumps(self.__dict__, sort_keys=True)
        return node

    def get_remote_chain(self):
        """
        Get the whole block_chain from a remote.
        """
        try:
            response = requests.get(
                '{}Nodes/chain'.format(self._node_address))
        except ConnectionError:
            message = "Can't get remote chain"
            raise HttpErrors(message)

        return response.json()

    @classmethod
    def build_node_from_request(cls, request):
        """
        Node Builder: Returns a node instance for a given request. 
        Raises an exception is Instance couldn't be created.
        """
        try:
            node_address = request.get_json()["node_address"]
            node_name = request.get_json()["node_name"]
        except:
            message = "No node_address or name was provided"
            raise NodeError(message)

        new_node = Node(node_address, node_name)
        return new_node

    @staticmethod
    def serialize_nodes(str_nodes, self_node):
        """
        Serialize the received nodes in string format to Node
        """
        serialized_nodes = []
        try:
            received_nodes = str_nodes
            for node in received_nodes:

                if node != self_node:
                    node = json.loads(node)
                    serialized_nodes.append(
                        Node(node.get('_node_address'), node.get('_node_name'))
                    )
                else:
                    continue

        except Exception as e:
            return SerializeNodeError("Can't serialize the node" + str(e))

        return serialized_nodes

    @property
    def node_address(self):
        return self._node_address

    @property
    def node_name(self):
        return self._node_name
