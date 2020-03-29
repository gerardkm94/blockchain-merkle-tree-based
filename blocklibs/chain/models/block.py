from blockchain.app import api_block
from flask_restplus import fields

block_resource_fields = api_block.model('Block', {})

block_tamper_resource_fields = api_block.model(
    'BlockTamper', {
        'author': fields.String,
        'content': fields.String,
        'block_index': fields.Integer,
        'transaction_index': fields.Integer,
    }
)
