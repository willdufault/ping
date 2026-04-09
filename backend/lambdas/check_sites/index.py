"""TODO: check status of url, maybe batch"""

import requests


def main(event, context):
    # TODO:
    # 1. read list of urls from event
    # 2. use thread pool to ping each one with 2s timeout (try 2x per)
    # 3. read dynamo table name from env var passed from IaC
    # 4. write the results to dynamo (BATCH WRITES)

    response = requests.get("https://www.google.com")
    return {"statusCode": 200, "body": response.status_code}
