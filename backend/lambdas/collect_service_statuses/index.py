"""
Check AWS service health in parallel across regions, storing one DynamoDB item
per (region, service): a status of healthy, degraded, outage or unknown, plus a
message explaining anything that is not healthy.
get_service_statuses reads this layout and shares the `regions` env var, but
cannot import this code since each Lambda bundles its own directory.
"""

import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import cache
from os import environ as env

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import (
    ClientError,
    ConnectTimeoutError,
    ConnectionClosedError,
    EndpointConnectionError,
    ReadTimeoutError,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGIONS = [region.strip() for region in env["regions"].split(",")]
THREAD_COUNT = 4
MAX_DATAPOINTS = 48

HEALTHY = "healthy"
DEGRADED = "degraded"
OUTAGE = "outage"
UNKNOWN = "unknown"

# Socket timeout, distinct from the latency threshold that marks a call degraded.
TIMEOUT_SECONDS = 5
LATENCY_THRESHOLD_SECONDS = 3

# Throttle codes from botocore's _retry.json. Several arrive as 503
# (RequestLimitExceeded, EC2ThrottledException, SlowDown) rather than 429, so the
# code has to be checked, not just the status. LimitExceededException is left out:
# an account quota, not a service fault.
THROTTLE_CODES = [
    "Throttling",
    "ThrottlingException",
    "ThrottledException",
    "RequestThrottledException",
    "RequestThrottled",
    "TooManyRequests",
    "TooManyRequestsException",
    "RequestLimitExceeded",
    "EC2ThrottledException",
    "SlowDown",
    "BandwidthLimitExceeded",
    "ProvisionedThroughputExceededException",
]

# Listed one by one since the two pairs share no base class, and catching either
# base would also catch SSLError and ProxyConnectionError, which are our fault.
UNREACHABLE_ERRORS = (
    EndpointConnectionError,
    ConnectTimeoutError,
    ReadTimeoutError,
    ConnectionClosedError,
)

TABLE_NAME = env["table_name"]
TABLE_REGION = env["table_region"]

# One attempt, so a throttle or 5xx is observed rather than retried away.
config = Config(
    connect_timeout=TIMEOUT_SECONDS,
    read_timeout=TIMEOUT_SECONDS,
    retries={"max_attempts": 1, "mode": "standard"},
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


def timed_check(
    check_function: Callable[[str], None], region: str
) -> tuple[float, Exception | None]:
    started_at = time.perf_counter()
    error: Exception | None = None
    try:
        check_function(region)
    except Exception as raised:
        error = raised
    return time.perf_counter() - started_at, error


def classify_check(elapsed: float, error: Exception | None) -> tuple[str, str | None]:
    if error is None:
        if elapsed < LATENCY_THRESHOLD_SECONDS:
            return HEALTHY, None
        return DEGRADED, "Increased latency"

    if isinstance(error, ClientError):
        code = error.response.get("Error", {}).get("Code", "")
        metadata = error.response.get("ResponseMetadata")
        http_status = metadata.get("HTTPStatusCode", 0) if metadata else 0

        # Checked before 5xx because three of those codes are 503s.
        if http_status == 429 or code in THROTTLE_CODES:
            return DEGRADED, "Throttling"

        if http_status >= 500:
            return OUTAGE, "Service error"

    if isinstance(error, UNREACHABLE_ERRORS):
        return OUTAGE, "Service unreachable"

    # Credential, region and param errors land here: our fault, not an outage.
    return UNKNOWN, str(error)


def write_to_db(
    service_name: str, region: str, status: str, message: str | None, timestamp: int
) -> None:
    # Read-modify-write is not atomic, so a concurrent invoke can drop a datapoint.
    item_key = {"PK": f"REGION#{region}", "SK": f"SERVICE#{service_name}"}
    item = dynamodb_table.get_item(Key=item_key)
    status_history = item.get("Item", {}).get("status_history", [])
    assert isinstance(status_history, list)
    status_history.append({"timestamp": timestamp, "status": status, "message": message})
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
                    future = executor.submit(timed_check, check_function, region)
                    futures.append((service_name, region, future))

            for service_name, region, future in futures:
                elapsed, error = future.result()
                status, message = classify_check(elapsed, error)
                logger.info(f"Check {service_name}/{region}: {status} - {message}")

                # Infra is in us-west-2, so isolated if us-east-1/us-east-2 impacted.
                try:
                    write_to_db(service_name, region, status, message, timestamp)
                except Exception as write_error:
                    logger.error(
                        f"Failed to write {service_name}/{region}: {write_error}"
                    )
        return {"statusCode": 200}
    except Exception as error:
        logger.exception(error)
        return {"statusCode": 500}
