"""
Check AWS service health in parallel across regions, storing one DynamoDB item
per (region, service): 200 healthy, 400 service failure, 500 unknown.
get_service_statuses reads this layout and shares the `regions` env var, but
cannot import this code since each Lambda bundles its own directory.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from functools import cache
from os import environ as env

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGIONS = [region.strip() for region in env["regions"].split(",")]
THREAD_COUNT = 4
RETRY_COUNT = 1
TIMEOUT_SECONDS = 3
MAX_DATAPOINTS = 48

SUCCESS_CODE = 200
FAILURE_CODE = 400
SERVER_ERROR_CODE = 500

TABLE_NAME = env["table_name"]
TABLE_REGION = env["table_region"]

config = Config(
    connect_timeout=TIMEOUT_SECONDS,
    read_timeout=TIMEOUT_SECONDS,
    retries={"max_attempts": 1 + RETRY_COUNT, "mode": "standard"},
)


@cache
def get_client(service_name: str, region: str) -> BaseClient:
    return boto3.client(service_name, config=config, region_name=region)  # type:ignore


dynamodb_table = boto3.resource("dynamodb", region_name=TABLE_REGION).Table(TABLE_NAME)


def check_ec2(region: str) -> None:
    ec2 = get_client("ec2", region)
    ec2.describe_instances()  # type:ignore


def check_s3(region: str) -> None:
    s3 = get_client("s3", region)
    s3.list_buckets()  # type:ignore


def check_lambda(region: str) -> None:
    lambda_client = get_client("lambda", region)
    lambda_client.list_functions(MaxItems=1)  # type:ignore


def check_dynamodb(region: str) -> None:
    dynamodb = get_client("dynamodb", region)
    dynamodb.list_tables(Limit=1)  # type:ignore


def check_cloudfront(region: str) -> None:
    cloudfront = get_client("cloudfront", region)
    cloudfront.list_distributions()  # type:ignore


def write_to_db(
    service_name: str, region: str, status_code: int, timestamp: int
) -> None:
    # Read-modify-write is not atomic, so a concurrent invoke can drop a datapoint.
    item_key = {"PK": f"REGION#{region}", "SK": f"SERVICE#{service_name}"}
    item = dynamodb_table.get_item(Key=item_key)
    status_history = item.get("Item", {}).get("status_history", [])
    assert isinstance(status_history, list)
    status_history.append({"timestamp": timestamp, "status_code": status_code})
    status_history = status_history[-MAX_DATAPOINTS:]
    dynamodb_table.put_item(Item={**item_key, "status_history": status_history})


def main(event, context):
    try:
        timestamp = int(time.time())
        service_checks = {
            "ec2": check_ec2,
            "s3": check_s3,
            "lambda": check_lambda,
            "dynamodb": check_dynamodb,
            "cloudfront": check_cloudfront,
        }
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            futures = []
            for service_name, check_function in service_checks.items():
                for region in REGIONS:
                    future = executor.submit(check_function, region)
                    futures.append((service_name, region, future))

            for service_name, region, future in futures:
                try:
                    future.result()
                    logger.info(
                        f"Check succeeded {service_name}/{region}: {SUCCESS_CODE}"
                    )
                    status_code = SUCCESS_CODE
                # ClientError means the service answered with an error. Anything else
                # means we never got an answer, so blame us rather than the service.
                except ClientError as error:
                    logger.warning(
                        f"Check failed {service_name}/{region}: {FAILURE_CODE} - {error}"
                    )
                    status_code = FAILURE_CODE
                except Exception as error:
                    logger.error(
                        f"Check failed {service_name}/{region}: {SERVER_ERROR_CODE} - {error}"
                    )
                    status_code = SERVER_ERROR_CODE

                # Infra is in us-west-2, so isolated if us-east-1/us-east-2 impacted.
                try:
                    write_to_db(service_name, region, status_code, timestamp)
                except Exception as error:
                    logger.error(f"Failed to write {service_name}/{region}: {error}")
        return {"statusCode": SUCCESS_CODE}
    except Exception as error:
        logger.exception(error)
        return {"statusCode": SERVER_ERROR_CODE}
