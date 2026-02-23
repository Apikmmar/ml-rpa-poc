from aws_cdk import (
    aws_s3 as s3,
    RemovalPolicy,
    Stack
)
from constructs import Construct

from .dynamo_db_stack import DynamoDBStack
from .lambda_function_stack import LambdaStack
from .api_gateway_stack import ApiGatewayStack

class MlRpaPocStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        bucket = s3.Bucket(self, "MLBucket",
            bucket_name="rpa-s3-ml-poc",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=True,
            cors=[s3.CorsRule(
                allowed_methods=[s3.HttpMethods.PUT],
                allowed_origins=["*"],
                allowed_headers=["*"],
                exposed_headers=["ETag"]
            )]
        )

        dynamo_db_stack = DynamoDBStack(self, "DynamoDBStack")
        lambda_stack = LambdaStack(self, "LambdaStack", dynamo_db_stack=dynamo_db_stack, bucket=bucket)
        ApiGatewayStack(self, "ApiGatewayStack", lambda_stack=lambda_stack)