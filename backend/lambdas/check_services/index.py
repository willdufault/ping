"""
Check health of AWS services across regions using parallel API calls. Returns
status codes for each service: 200 for healthy, 400 for service failures, 500
for server/internal failures.
"""

import logging
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from functools import cache
from os import environ as env

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import BotoCoreError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = env["table_name"]
TABLE_REGION = env["table_region"]

REGIONS = ["us-east-1", "us-east-2"]
THREAD_COUNT = 4
RETRY_COUNT = 1
TIMEOUT_SECONDS = 3
MAX_DATAPOINTS = 48

SUCCESS_CODE = 200
FAILURE_CODE = 400
SERVER_ERROR_CODE = 500

config = Config(
    connect_timeout=TIMEOUT_SECONDS,
    read_timeout=TIMEOUT_SECONDS,
    retries={"max_attempts": RETRY_COUNT, "mode": "standard"},
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
    # NOTE: Read-modify-write is not atomic. This is acceptable because EventBridge
    # triggers this Lambda every 30 minutes, preventing concurrent invocations.
    item = dynamodb_table.get_item(Key={"PK": service_name, "SK": region})
    existing_responses = item.get("Item", {}).get("responses", [])
    assert isinstance(existing_responses, list)
    existing_responses.append({"timestamp": timestamp, "status_code": status_code})
    existing_responses = existing_responses[-MAX_DATAPOINTS:]
    dynamodb_table.put_item(
        Item={
            "PK": service_name,
            "SK": region,
            "responses": existing_responses,
        }
    )


def main(event, context):
    try:
        timestamp = int(time.time())
        responses_by_region = defaultdict(dict)
        service_checks = {
            "ec2": check_ec2,
            "s3": check_s3,
            "lambda": check_lambda,
            "dynamodb": check_dynamodb,
            "cloudfront": check_cloudfront,
        }
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            futures = {
                (service_name, region): executor.submit(check_function, region)
                for service_name, check_function in service_checks.items()
                for region in REGIONS
            }
            for (service_name, region), future in futures.items():
                try:
                    future.result()
                    logger.info(
                        f"Check succeeded {service_name}/{region}: {SUCCESS_CODE}"
                    )
                    responses_by_region[region][service_name] = SUCCESS_CODE
                except BotoCoreError as error:
                    logger.warning(
                        f"Check failed {service_name}/{region}: {FAILURE_CODE} - {error}"
                    )
                    responses_by_region[region][service_name] = FAILURE_CODE
                except Exception as error:
                    logger.error(
                        f"Check failed {service_name}/{region}: {SERVER_ERROR_CODE} - {error}"
                    )
                    responses_by_region[region][service_name] = SERVER_ERROR_CODE
        for region, responses in responses_by_region.items():
            for service_name, status_code in responses.items():
                try:
                    # TODO: if ddb is down this wont be written and ui will not reflect this
                    # need to have some logic in ui or something or backfill data for missing data
                    write_to_db(service_name, region, status_code, timestamp)
                except Exception as error:
                    logger.error(f"Failed to write {service_name}/{region}: {error}")
        return {"statusCode": 200}
    except Exception as error:
        logger.error(f"{type(error).__name__}: {error}")
        return {"statusCode": 500}
