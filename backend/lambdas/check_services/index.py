"""Check health of AWS services across regions using parallel API calls.
Returns status codes for each service: 200 for healthy, 400/500 for failures.
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGIONS = ["us-east-1", "us-east-2"]

THREAD_COUNT = 4
RETRY_COUNT = 1
TIMEOUT_SECONDS = 3
COOLDOWN_SECONDS = 3

SUCCESS_CODE = 200
FAILURE_CODE = 400
SERVER_ERROR_CODE = 500

config = Config(
    connect_timeout=TIMEOUT_SECONDS,
    read_timeout=TIMEOUT_SECONDS,
    retries={"max_attempts": RETRY_COUNT, "mode": "standard"},
)
ec2 = boto3.client("ec2", config=config)
lambda_client = boto3.client("lambda", config=config)
s3 = boto3.client("s3", config=config)
dynamodb = boto3.client("dynamodb", config=config)
cloudfront = boto3.client("cloudfront", config=config)


def check_ec2() -> int:
    ec2.describe_instances()
    return SUCCESS_CODE


def check_s3() -> int:
    s3.list_buckets()
    return SUCCESS_CODE


def check_lambda() -> int:
    lambda_client.list_functions(MaxItems=1)
    return SUCCESS_CODE


def check_dynamodb() -> int:
    dynamodb.list_tables(Limit=1)
    return SUCCESS_CODE


def check_cloudfront() -> int:
    cloudfront.list_distributions()
    return SUCCESS_CODE


# TODO: schedule lambda
# TODO: add logging
def main(event, context):
    responses = {}
    service_checks = {
        "EC2": check_ec2,
        "S3": check_s3,
        "Lambda": check_lambda,
        "DynamoDB": check_dynamodb,
        "CloudFront": check_cloudfront,
    }
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        futures = {
            service_name: executor.submit(check_function)
            for service_name, check_function in service_checks.items()
        }
        for service_name, future in futures.items():
            try:
                status_code = future.result()
                logger.info(f"{service_name}: {status_code}")
                responses[service_name] = status_code
            except BotoCoreError as error:
                logger.warning(f"{service_name}: {FAILURE_CODE} - {error}")
                responses[service_name] = FAILURE_CODE
            except Exception as error:
                logger.error(f"{service_name}: {SERVER_ERROR_CODE} - {error}")
                responses[service_name] = SERVER_ERROR_CODE
    return {"statusCode": 200, "body": json.dumps(responses)}
