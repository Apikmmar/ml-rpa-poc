import os
import uuid
import boto3
import httpx
from decimal import Decimal
from datetime import datetime, timezone
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

dynamodb = boto3.resource('dynamodb')

PREFIX = os.environ.get('TABLE_PREFIX', 'RPA-')

HISTORY_TABLE_NAME = os.environ['HISTORY_TABLE_NAME']
HISTORY_TABLE = dynamodb.Table(HISTORY_TABLE_NAME)

AIRTABLE_TOKEN = os.environ['AIRTABLE_TOKEN']
AIRTABLE_BASE_ID = os.environ['AIRTABLE_BASE_ID']
AIRTABLE_BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

AIRTABLE_TABLES = [
    'Orders',
    'Stocks',
    'Order_Items',
    'Picklists',
    'AuditLogs',
    'Stock_Transfers',
    'Exceptions',
    'Notifications',
    'Backorders',
]

logger = Logger()
tracer = Tracer()

@tracer.capture_lambda_handler
def lambda_handler(event, context: LambdaContext):
    sync_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    results = {}

    try:
        for table in AIRTABLE_TABLES:
            records = fetchAllRecords(table)
            if not records:
                results[table] = {'count': 0, 'status': 'SUCCESS'}
                continue
            
            count = syncTableData(table, records)
            results[table] = {'count': count, 'status': 'SUCCESS'}

        createHistoryData(sync_id, now, results)

        return {'status': True, 'syncId': sync_id, 'results': results}

    except Exception as e:
        tracer.put_annotation("lambda_error", "true")
        tracer.put_annotation("lambda_name", context.function_name)
        tracer.put_metadata("event", event)
        tracer.put_metadata("message", str(e))
        logger.exception({"message": str(e)})
        return {'status': False, 'message': "The server encountered an unexpected condition that prevented it from fulfilling your request."}

@tracer.capture_method
def createHistoryData(sync_id, now, results):
    HISTORY_TABLE.put_item(Item={
            'syncHistoryId': sync_id,
            'createdAt': now,
            'createdBy': "System",
            'updatedAt': now,
            'updatedBy': "System",
            'status': 'SUCCESS' if all(v['status'] == 'SUCCESS' for v in results.values()) else 'PARTIAL',
            'results': {k: str(v) for k, v in results.items()}
        })

@tracer.capture_method
def fetchAllRecords(table_name: str) -> list:
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}"}
    records, offset = [], None

    with httpx.Client(timeout=30) as client:
        while True:
            params = {"offset": offset} if offset else {}
            resp = client.get(f"{AIRTABLE_BASE_URL}/{table_name}", headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            records.extend(data.get("records", []))
            offset = data.get("offset")
            if not offset:
                break

    return records

@tracer.capture_method
def camelCaseID(name: str) -> str:
    parts = name.split('_')
    return parts[0][0].lower() + parts[0][1:] + ''.join(p.capitalize() for p in parts[1:]) + 'Id'

@tracer.capture_method
def floatToDecimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: floatToDecimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [floatToDecimal(v) for v in obj]
    return obj

@tracer.capture_method
def syncTableData(table_name: str, records: list) -> int:
    ddb_table = dynamodb.Table(f"{PREFIX}{table_name}")
    pk = camelCaseID(table_name)

    with ddb_table.batch_writer() as batch:
        for record in records:
            item = floatToDecimal({pk: record['id'], **record.get('fields', {})})

            batch.put_item(Item=item)

    return len(records)