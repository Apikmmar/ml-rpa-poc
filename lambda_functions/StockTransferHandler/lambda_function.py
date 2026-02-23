import os
import json
import boto3
from botocore.config import Config
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

s3 = boto3.client(
    's3',
    region_name='ap-southeast-1',
    config=Config(signature_version='s3v4'),
    endpoint_url='https://s3.ap-southeast-1.amazonaws.com'
)
dynamodb = boto3.resource('dynamodb')

S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
_TABLE_NAME = os.environ.get('_TABLE_NAME')

_TABLE = dynamodb.Table(_TABLE_NAME)

logger = Logger()
tracer = Tracer()

@tracer.capture_lambda_handler
def lambda_handler(event, context: LambdaContext):
    try:
        

        return {
            'statusCode': 200,
            'message': 'Successfully',
        }

    except Exception as e:
        tracer.put_annotation("lambda_error", "true")
        tracer.put_annotation("lambda_name", context.function_name)
        tracer.put_metadata("event", event)
        tracer.put_metadata("message", str(e))
        logger.exception({"message": str(e)})
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'status': False, 'message': "The server encountered an unexpected condition that prevented it from fulfilling your request."})
        }

# StockTransferValidator + TransferAutoApproval → 1 Lambda: StockTransferHandler
# Both trigger on Stock_Transfers INSERT. Natural sequence — validate first, then approve:

# Validate (same location/rack, qty < 1) → set Failed

# If valid: qty ≤ 30 → auto Complete, qty > 30 → set Pending + notify