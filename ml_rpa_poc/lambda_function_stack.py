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

        # --- Automation Lambdas ---
        automation_defaults = dict(
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(60),
            memory_size=256,
            layers=[powertools_layer],
            environment={"TABLE_PREFIX": PREFIX}
        )

        # 1. ValidateNewOrder — Orders INSERT
        validate_order = lambda_.Function(self, "ValidateNewOrderLambda",
            function_name=f"{PREFIX}ValidateNewOrder",
            code=lambda_.Code.from_asset("lambda_functions/ValidateNewOrder"),
            **automation_defaults
        )
        validate_order.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Orders'],
            starting_position=lambda_.StartingPosition.LATEST,
            filters=[lambda_.FilterCriteria.filter({"eventName": lambda_.FilterRule.is_equal("INSERT")})]
        ))

        # 2. CheckValidatedStock — Orders status → Validated
        check_stock = lambda_.Function(self, "CheckValidatedStockLambda",
            function_name=f"{PREFIX}CheckValidatedStock",
            code=lambda_.Code.from_asset("lambda_functions/CheckValidatedStock"),
            **automation_defaults
        )
        check_stock.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Orders'],
            starting_position=lambda_.StartingPosition.LATEST,
            filters=[lambda_.FilterCriteria.filter({
                "eventName": lambda_.FilterRule.is_equal("MODIFY"),
                "dynamodb": {"NewImage": {"status": {"S": lambda_.FilterRule.is_equal("Validated")}}}
            })]
        ))

        # 3. GenerateNewPicklist — Orders status → Stock Confirmed
        gen_picklist = lambda_.Function(self, "GenerateNewPicklistLambda",
            function_name=f"{PREFIX}GenerateNewPicklist",
            code=lambda_.Code.from_asset("lambda_functions/GenerateNewPicklist"),
            **automation_defaults
        )
        gen_picklist.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Orders'],
            starting_position=lambda_.StartingPosition.LATEST,
            filters=[lambda_.FilterCriteria.filter({
                "eventName": lambda_.FilterRule.is_equal("MODIFY"),
                "dynamodb": {"NewImage": {"status": {"S": lambda_.FilterRule.is_equal("Stock Confirmed")}}}
            })]
        ))

        # 4. PicklistHandler — Picklists all events (INSERT + MODIFY)
        picklist_handler = lambda_.Function(self, "PicklistHandlerLambda",
            function_name=f"{PREFIX}PicklistHandler",
            code=lambda_.Code.from_asset("lambda_functions/PicklistHandler"),
            **automation_defaults
        )
        picklist_handler.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Picklists'],
            starting_position=lambda_.StartingPosition.LATEST
        ))

        # 5. StockTransferHandler — Stock_Transfers INSERT
        transfer_handler = lambda_.Function(self, "StockTransferHandlerLambda",
            function_name=f"{PREFIX}StockTransferHandler",
            code=lambda_.Code.from_asset("lambda_functions/StockTransferHandler"),
            **automation_defaults
        )
        transfer_handler.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Stock_Transfers'],
            starting_position=lambda_.StartingPosition.LATEST,
            filters=[lambda_.FilterCriteria.filter({"eventName": lambda_.FilterRule.is_equal("INSERT")})]
        ))

        # 6. TransferCompletionHandler — Stock_Transfers status → Completed
        transfer_completion = lambda_.Function(self, "TransferCompletionHandlerLambda",
            function_name=f"{PREFIX}TransferCompletionHandler",
            code=lambda_.Code.from_asset("lambda_functions/TransferCompletionHandler"),
            **automation_defaults
        )
        transfer_completion.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Stock_Transfers'],
            starting_position=lambda_.StartingPosition.LATEST,
            filters=[lambda_.FilterCriteria.filter({
                "eventName": lambda_.FilterRule.is_equal("MODIFY"),
                "dynamodb": {"NewImage": {"status": {"S": lambda_.FilterRule.is_equal("Completed")}}}
            })]
        ))

        # 7. StockChangeHandler — Stocks MODIFY
        stock_change = lambda_.Function(self, "StockChangeHandlerLambda",
            function_name=f"{PREFIX}StockChangeHandler",
            code=lambda_.Code.from_asset("lambda_functions/StockChangeHandler"),
            **automation_defaults
        )
        stock_change.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Stocks'],
            starting_position=lambda_.StartingPosition.LATEST,
            filters=[lambda_.FilterCriteria.filter({"eventName": lambda_.FilterRule.is_equal("MODIFY")})]
        ))

        # 8. ExceptionHandler — Exceptions INSERT
        exception_handler = lambda_.Function(self, "ExceptionHandlerLambda",
            function_name=f"{PREFIX}ExceptionHandler",
            code=lambda_.Code.from_asset("lambda_functions/ExceptionHandler"),
            **automation_defaults
        )
        exception_handler.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Exceptions'],
            starting_position=lambda_.StartingPosition.LATEST,
            filters=[lambda_.FilterCriteria.filter({"eventName": lambda_.FilterRule.is_equal("INSERT")})]
        ))

        # 9. ShippedOrderNotification — Orders status → Shipped
        shipped_notif = lambda_.Function(self, "ShippedOrderNotificationLambda",
            function_name=f"{PREFIX}ShippedOrderNotification",
            code=lambda_.Code.from_asset("lambda_functions/ShippedOrderNotification"),
            **automation_defaults
        )
        shipped_notif.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Orders'],
            starting_position=lambda_.StartingPosition.LATEST,
            filters=[lambda_.FilterCriteria.filter({
                "eventName": lambda_.FilterRule.is_equal("MODIFY"),
                "dynamodb": {"NewImage": {"status": {"S": lambda_.FilterRule.is_equal("Shipped")}}}
            })]
        ))

        # 10. UpdateOrderCancellation — Orders status → Cancelled or Expired
        order_cancellation = lambda_.Function(self, "UpdateOrderCancellationLambda",
            function_name=f"{PREFIX}UpdateOrderCancellation",
            code=lambda_.Code.from_asset("lambda_functions/UpdateOrderCancellation"),
            **automation_defaults
        )
        order_cancellation.add_event_source(lambda_events.DynamoEventSource(
            dynamo_db_stack.tables['Orders'],
            starting_position=lambda_.StartingPosition.LATEST,
            filters=[lambda_.FilterCriteria.filter({
                "eventName": lambda_.FilterRule.is_equal("MODIFY"),
                "dynamodb": {"NewImage": {"status": {"S": ["Cancelled", "Expired"]}}}
            })]
        ))

        # Grant all automation Lambdas read/write to all tables
        automation_lambdas = [
            validate_order, check_stock, gen_picklist, picklist_handler,
            transfer_handler, transfer_completion, stock_change,
            exception_handler, shipped_notif, order_cancellation
        ]
        for fn in automation_lambdas:
            for table in dynamo_db_stack.tables.values():
                table.grant_read_write_data(fn)
                table.grant_stream_read(fn)
