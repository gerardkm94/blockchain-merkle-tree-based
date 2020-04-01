from flask_restplus import fields, Namespace

api_nodes = Namespace(
    'Nodes', description='Nodes operations')

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