import json


class Transaction():

    def __init__(self, author, content, timestamp):

        self.author = author
        self.content = content
        self.timestamp = timestamp

    @property
    def get_transaction(self):

        transaction = json.dumps(self.__dict__, sort_keys=True)

        return transaction
