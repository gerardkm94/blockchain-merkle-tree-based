

import json
import datetime
import requests


class Node():

    def __init__(self, node_address, node_name):
        self._node_address = node_address
        self._node_name = node_name
        self._time_stamp = datetime.datetime.now()

    def get_node_info(self):
        node = json.dumps(self.__dict__, sort_keys=True)
        return node

    def get_remote_chain(self):
        """
        Get the whole block_chain from a remote.
        """
        response = requests.get(
            'http://{}/Nodes/chain'.format(self._node_address))

        return response.json()
