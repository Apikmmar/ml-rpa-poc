from aws_cdk import (
    Stack,
    Duration,
    BundlingOptions,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_events,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
)
from constructs import Construct
from .config import PREFIX

class LambdaStack(Construct):

    def __init__(self, scope: Construct, construct_id: str, dynamo_db_stack, bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        powertools_layer = lambda_.LayerVersion.from_layer_version_arn(
            self, "PowertoolsLayer",
            layer_version_arn="arn:aws:lambda:ap-southeast-1:017000801446:layer:AWSLambdaPowertoolsPythonV2:68"
        )

        httpx_layer = lambda_.LayerVersion(
            self, "HttpxLayer",
            code=lambda_.Code.from_asset(
                "layers/httpx",
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_11.bundling_image,
                    command=["bash", "-c", "pip install -r requirements.txt -t /asset-output/python"]
                )
            ),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="httpx layer"
        )
        
        presign_lambda = lambda_.Function(
            self, "GeneratePresignedURLLambda",
            function_name=f"{PREFIX}GeneratePresignedURL",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("lambda_functions/GeneratePresignedURL"),
            timeout=Duration.seconds(300),
            memory_size=128,
            layers=[powertools_layer],
            environment={
                "S3_BUCKET_NAME": bucket.bucket_name
            }
        )
        
        bucket.grant_read_write(presign_lambda)
        bucket.grant_put(presign_lambda)
        self.presign_lambda = presign_lambda

        sync_lambda = lambda_.Function(
            self, "SyncAirtableDataLambda",
            function_name=f"{PREFIX}SyncAirtableData",
            description="Lambda function to sync data from Airtable to DynamoDB",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("lambda_functions/SyncAirtableData"),
            timeout=Duration.seconds(300),
            memory_size=512,
            layers=[powertools_layer, httpx_layer],
            environment={
                "AIRTABLE_TOKEN": os.environ["AIRTABLE_TOKEN"],
                "AIRTABLE_BASE_ID": os.environ["AIRTABLE_BASE_ID"],
                "HISTORY_TABLE_NAME": f"{PREFIX}SyncHistory",
                "TABLE_PREFIX": PREFIX
            }
        )

        csv_lambda = lambda_.Function(
            self, "ProcessOrdersCSVLambda",
            function_name=f"{PREFIX}ProcessOrdersCSV",
            description="Lambda function to read order from CSV in S3",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("lambda_functions/ProcessOrdersCSV"),
            timeout=Duration.seconds(300),
            memory_size=512,
            layers=[powertools_layer, httpx_layer],
            environment={
                "TABLE_PREFIX": PREFIX,
                "S3_BUCKET_NAME": bucket.bucket_name,
                "FASTAPI_URL": "https://ml-rpa-poc.onrender.com"
            }
        )

        bucket.grant_read_write(csv_lambda)
        
        csv_lambda.add_event_source(lambda_events.S3EventSource(
            bucket,
            events=[s3.EventType.OBJECT_CREATED],
            filters=[s3.NotificationKeyFilter(prefix="orders/", suffix=".csv")]
        ))

        # Grant DynamoDB read/write to all synced tables
        for table in dynamo_db_stack.tables.values():
            table.grant_read_write_data(sync_lambda)

        # EventBridge rule: trigger every 7 days
        rule = events.Rule(
            self, "WeeklySyncRule",
            rule_name=f"{PREFIX}WeeklySyncRule",
            schedule=events.Schedule.rate(Duration.days(7)),
            description="Trigger Airtable sync every 7 days"
        )
        rule.add_target(targets.LambdaFunction(sync_lambda))
