"""TODO: check status of endpoints, ADD DESC HERE"""

"""
TODO: get endpoint won't work, need to do list call for each service & region
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGIONS = ["us-east-1", "us-east-2"]
SERVICES = ["ec2", "lambda", "s3", "dynamodb", "rds", "sqs"]
THREAD_COUNT = 4
RETRY_COUNT = 2
TIMEOUT_SECONDS = 2
COOLDOWN_SECONDS = 2
SUCCESS_CODE = 200
SERVER_ERROR_CODE = 500


# TODO: add logging
def check_endpoint(endpoint: str) -> int:
    status_code = SERVER_ERROR_CODE
    for _ in range(RETRY_COUNT):
        try:
            response = requests.get(endpoint, timeout=TIMEOUT_SECONDS)
        except Exception:
            time.sleep(COOLDOWN_SECONDS)
            continue

        status_code = response.status_code
        if status_code == SUCCESS_CODE:
            break
    return status_code


# TODO: schedule lambda
def main(event, context):
    responses = {}
    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        endpoints = [
            f"https://{service}.{region}.amazonaws.com"
            for region in REGIONS
            for service in SERVICES
        ]
        futures = {
            endpoint: executor.submit(check_endpoint, endpoint)
            for endpoint in endpoints
        }
        for endpoint, future in futures.items():
            status_code = future.result()
            responses[endpoint] = status_code
    return {"statusCode": 200, "body": json.dumps(responses)}
