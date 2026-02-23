import os
import csv
import boto3
import httpx
from datetime import datetime
from io import StringIO
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

s3 = boto3.client('s3')
logger = Logger()
tracer = Tracer()

FASTAPI_URL = os.environ.get('FASTAPI_URL')

@tracer.capture_lambda_handler
def lambda_handler(event, context: LambdaContext):
    results = []
    today = datetime.today().strftime('%Y-%m-%d')

    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            obj = s3.get_object(Bucket=bucket, Key=key)
            content = obj['Body'].read().decode('utf-8')
            reader = csv.DictReader(StringIO(content))

            orders = {}
            for row in reader:
                order_key = (row['customer_email'], row['customer_id'], row['priority'])
                if order_key not in orders:
                    orders[order_key] = []
                orders[order_key].append({'sku': row['sku'], 'qty': int(row['qty'])})

            with httpx.Client(timeout=30) as client:
                for (customer_email, customer_id, priority), items in orders.items():
                    payload = {
                        'customer_email': customer_email,
                        'customer_id': customer_id,
                        'priority': priority,
                        'items': items
                    }
                    resp = client.post(f"{FASTAPI_URL}/orders", json=payload, follow_redirects=False)
                    results.append({'order': customer_id, 'status': resp.status_code, 'response': resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text})

            processed_key = key.replace('orders/', f'processed/{today}/', 1)
            s3.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': key}, Key=processed_key)
            s3.delete_object(Bucket=bucket, Key=key)

        return {
            'status': True, 
            'results': results
        }

    except Exception as e:
        tracer.put_annotation("lambda_error", "true")
        tracer.put_annotation("lambda_name", context.function_name)
        tracer.put_metadata("event", event)
        tracer.put_metadata("message", str(e))
        logger.exception({"message": str(e)})
        return {'status': False, 'message': "The server encountered an unexpected condition that prevented it from fulfilling your request."}
