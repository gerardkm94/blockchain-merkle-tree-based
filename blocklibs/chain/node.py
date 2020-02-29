

import json
import datetime

from flask import request


class Node():

    def __init__(self, node_address, node_name):
        self._node_address = ""
        self._node_name = ""
        self._time_stamp = datetime.datetime.now()

    def get_node_info(self):
        node = json.dumps(self.__dict__, sort_keys=True)
        return node

    def get_remote_chain(self):
        """
        Get the whole block_chain from a remote.
        """
        response = request.get('http://{}/chain'.format(self._node_address))
        chain_length = response.json()['length']
        chain_data = response.json()['chain']

        return chain_length, chain_data
