from flask import request
import json


class Nodes():

    def __init__(self, blockchain, peers):
        self.blockchain = blockchain
        self.peers = peers

    def consensus(self):
        """
        Consensus Algorithm. If a longer chain is found, it will be replaced with it.
        """

        longest_chain = None
        current_len = len(self.blockchain)

        for node in self.peers:
            chain_len, chain = self.get_chain(node)

            if chain_len > current_len:
                current_len = chain_len
                longest_chain = chain

        if longest_chain:
            self.blockchain = longest_chain
            return True

        return False

    def get_chain(self, node):
        response = request.get('http://{}/chain'.format(node))
        chain_length = response.json()['length']
        chain = response.json()['chain']

        return chain_length, chain
