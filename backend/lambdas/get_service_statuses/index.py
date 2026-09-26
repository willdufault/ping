"""
Return one region's status history from DynamoDB, keyed by service name. Items
are partitioned by region, so one query covers it and no pagination is needed.
region defaults to the first entry of the `regions` env var (REGIONS in
infra/app.py) and is rejected with 400 if unknown, so a typo is not mistaken
for no data.
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
            item["SK"].removeprefix("SERVICE#"): item.get("status_history", [])
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
