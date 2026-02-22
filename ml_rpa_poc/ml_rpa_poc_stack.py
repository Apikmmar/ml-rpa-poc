from aws_cdk import (
    aws_s3 as s3,
    RemovalPolicy,
    Stack
)
from constructs import Construct

from .dynamo_db_stack import DynamoDBStack
from .lambda_function_stack import LambdaStack

class MlRpaPocStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        bucket = s3.Bucket(self, "MLBucket",
            bucket_name="s3-ml-rpa-poc",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=True
        )

        dynamo_db_stack = DynamoDBStack(self, "DynamoDBStack")
        LambdaStack(self, "LambdaStack", dynamo_db_stack=dynamo_db_stack, bucket=bucket)