from flask_restplus import fields, Namespace

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
