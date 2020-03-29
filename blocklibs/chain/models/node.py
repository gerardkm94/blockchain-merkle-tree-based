from blockchain.app import api_nodes
from flask_restplus import fields

node_sync_resource_fields = api_nodes.model('Node',  {
    'node_address': fields.Url},
)

node_name_resource_fields = api_nodes.model('NameNode',  {
    'node_name': fields.String,
},
)

node_register_resource_fields = api_nodes.model('RegisterNode',  {
    'node_address': fields.Url,
    'node_name': fields.String, },
)
