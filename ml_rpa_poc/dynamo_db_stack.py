from aws_cdk import (
    RemovalPolicy,
    aws_dynamodb as dynamodb
)
from constructs import Construct
from .config import PREFIX

class DynamoDBStack(Construct):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        tableList = [
            'Orders',
            'Stocks',
            'Order_Items',
            'Picklists',
            'AuditLogs',
            'Stock_Transfers',
            'Exceptions',
            'Notifications',
            'Backorders',
            'GoodsReceipts',
            'Reports',
            'SyncHistory',
        ]
        
        self.tables = {}

        for table in tableList:
            parts = table.split('_')
            partition_key = parts[0][0].lower() + parts[0][1:] + ''.join(p.capitalize() for p in parts[1:]) + 'Id'
            
            ddb_table = dynamodb.Table(
                self, table,
                table_name=f"{PREFIX}{table}",
                partition_key=dynamodb.Attribute(name=partition_key, type=dynamodb.AttributeType.STRING),
                billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
                removal_policy=RemovalPolicy.DESTROY
            )
            self.tables[table] = ddb_table
            
            # if table == 'Orders':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'Stocks':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'Order_Items':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'Picklists':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'AuditLogs':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'Stock_Transfers':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'Exceptions':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'Notifications':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'Backorders':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'GoodsReceipts':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            # if table == 'Reports':
            #     ddb_table.add_global_secondary_index(
            #         partition_key=dynamodb.Attribute(name='status', type=dynamodb.AttributeType.STRING),
            #         index_name='-'.join(['gsi', 'status'])
            #     )
            
            