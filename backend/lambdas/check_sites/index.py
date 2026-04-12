"""TODO: check status of url, maybe batch"""

import json
import logging
from concurrent.futures import ThreadPoolExecutor

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

THREAD_COUNT = 30  # From https://github.com/aws-samples/aws-lambda-parallel-download
RETRY_COUNT = 2
TIMEOUT_SECONDS = 2


# TODO: add logging
def check_url(url: str) -> int:
    status_code = 400
    for _ in range(RETRY_COUNT):
        try:
            response = requests.get(url, timeout=TIMEOUT_SECONDS)
        except Exception:
            continue

        status_code = response.status_code
        if status_code == 200:
            break
    return status_code


def main(event, context):
    # TODO:
    # 1. read list of urls from event
    # 2. use thread pool to ping each one with 2s timeout (try 2x per)
    # 3. read dynamo table name from env var passed from IaC
    # 4. write the results to dynamo (BATCH WRITES)
    urls = [
        "https://www.google.com",
        "https://www.apple.com",
        "https://www.microsoft.com",
        "https://www.netflix.com",
        "https://www.example.com",
        "https://willdufault.dev",
        "https://www.NOT.REAL.2346sdfaosidhasdioasudhfiaushdf.com",
    ]
    responses = {}
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {url: executor.submit(check_url, url) for url in urls}
        for url, future in futures.items():
            status_code = future.result()
            responses[url] = status_code

    return {"statusCode": 200, "body": json.dumps(responses)}
