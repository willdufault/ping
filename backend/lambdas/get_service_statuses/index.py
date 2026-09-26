"""
Fetch service status history from DynamoDB for a single region. Returns a dict
mapping each service name to its full status_history list for the requested
region, keyed by the lowercase service name as stored.

Items are partitioned by region, written by collect_service_statuses, so one
Query returns the whole region. Each service is a single capped item, so the
result stays far below the 1MB page limit and no pagination is needed.

The region list comes from the `regions` environment variable, which CDK sets
from REGIONS in infra/app.py. region defaults to the first entry and is rejected
with 400 if it is not in the list, so a typo is not mistaken for "no data
collected yet".
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

REGIONS = [region.strip() for region in env["regions"].split(",")]
DEFAULT_REGION = REGIONS[0]

dynamodb_table = boto3.resource("dynamodb", region_name=TABLE_REGION).Table(TABLE_NAME)


def main(event, context):
    try:
        query_params = event.get("queryStringParameters") or {}
        region = query_params.get("region") or DEFAULT_REGION
        if region not in REGIONS:
            logger.warning(f"Rejected request for unknown region: {region}")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Unknown region: {region}"}),
            }
        query_response = dynamodb_table.query(
            KeyConditionExpression=Key("PK").eq(f"REGION#{region}")
        )
        statuses = {
            item["SK"].removeprefix("SERVICE#"): item["status_history"]
            for item in query_response["Items"]
        }
        # DynamoDB returns numbers as Decimal, which json cannot encode.
        return {
            "statusCode": 200,
            "body": json.dumps(statuses, default=int),
        }
    except Exception as error:
        logger.exception(error)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to fetch service statuses"}),
        }
