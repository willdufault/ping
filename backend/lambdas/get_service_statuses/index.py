"""
Fetch service status history from DynamoDB for a single region. Returns a dict
mapping each service name to its full status_history list for the requested
region, keyed by the lowercase service name as stored.

Items are partitioned by region, written by collect_service_statuses, so one
Query returns the whole region. Each service is a single capped item, so the
result stays far below the 1MB page limit and no pagination is needed.
"""

import json
import logging
from os import environ as env

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = env["table_name"]
TABLE_REGION = env["table_region"]
DEFAULT_REGION = "us-east-1"

dynamodb_table = boto3.resource("dynamodb", region_name=TABLE_REGION).Table(TABLE_NAME)


def main(event, context):
    try:
        region = (event.get("queryStringParameters") or {}).get(
            "region", DEFAULT_REGION
        )
        query_response = dynamodb_table.query(
            KeyConditionExpression=Key("PK").eq(f"REGION#{region}")
        )
        statuses = {
            item["SK"].removeprefix("SERVICE#"): item["status_history"]
            for item in query_response["Items"]
        }
        # status_history numbers come back as Decimal, which json cannot encode.
        return {
            "statusCode": 200,
            "body": json.dumps(statuses, default=float),
        }
    except Exception as error:
        logger.exception(error)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to fetch service statuses"}),
        }
