#!/usr/bin/env python

"""
Metrics Exporter for AWS API Gateway and Prometheus

This script fetches API Gateway metrics from AWS CloudWatch and exposes them 
via a Prometheus-compatible HTTP server for monitoring purposes. It uses the 
`boto3` AWS SDK to interact with AWS CloudWatch and `prometheus_client` to 
serve the metrics.

The script continuously retrieves the latest API Gateway metrics at regular 
intervals (configured by the user) and exposes them through a local HTTP server 
for Prometheus scraping.

Configuration:
-------------
The following environment variables are used to configure the behavior of the script:

- `AWS_REGION` (default: 'us-east-1') 
  : The AWS region where the API Gateway is located. If not set, the default region is 'us-east-1'.
  
- `API_ID` (required) 
  : The unique ID of the API Gateway for which metrics are to be fetched. This is a required environment variable.
  
- `API_STAGE` (default: '$default') 
  : The stage of the API Gateway. If not set, the default stage is '$default'.
  
- `REFRESH_INTERVAL` (default: 60) 
  : The time interval (in seconds) between metric refreshes. This defines how often the script fetches and updates metrics.
  
- `PORT` (default: 8200) 
  : The port on which the Prometheus-compatible HTTP server will run. Default is 8200, but can be adjusted based on your setup.
  
- `MAX_WORKERS` (default: 20) 
  : The maximum number of concurrent workers (threads) to use when fetching metrics.
    This helps control the parallelism and performance of the data retrieval process.

Dependencies:
------------
- boto3 : AWS SDK for Python, used for interacting with AWS CloudWatch.
- prometheus_client : Prometheus client library, used to expose metrics via HTTP.
- concurrent.futures : Used for handling concurrent metric fetching with threads.

Usage:
------
1. Set the required environment variables, especially `API_ID`.
2. Run the script as a standalone application.
3. Prometheus can scrape metrics exposed at `http://localhost:<PORT>/metrics`.

Maintainer:
-----------
Gabriel M. Dutra <dmdutra@proton.me>

"""


import boto3
import sys
import time
import os

from concurrent.futures import ThreadPoolExecutor, as_completed
from exporter.get_metrics import ApiGatewayMetrics
from exporter.prom_metrics import PromMetrics
from prometheus_client import start_http_server

# Configuration constants
REFRESH_INTERVAL = int(os.environ.get("REFRESH_INTERVAL", 60))
PORT = int(os.environ.get("PORT", 8200))
REGION = os.environ.get("AWS_REGION", "us-east-1")
API_ID = os.environ.get("API_ID")
API_STAGE = os.environ.get("API_STAGE", "$default")
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 20))

def main():
    """
    Main function to initialize and run the metrics exporter.

    This function initializes the `ApiGatewayMetrics` and `PromMetrics` objects,
    starts an HTTP server for Prometheus to scrape metrics, and continuously 
    fetches and updates the metrics at regular intervals.

    It will keep running indefinitely, refreshing the metrics as per the 
    specified `REFRESH_INTERVAL`.
    """

    apigw = ApiGatewayMetrics(API_ID, API_STAGE)
    prom = PromMetrics()

    try:
        start_http_server(PORT)
    except OSError as error:
        print(error)
        sys.exit(1)

    while True:
        prom.prometheus_metrics(apigw, MAX_WORKERS)
        time.sleep(REFRESH_INTERVAL)

if __name__ == '__main__':
    main()

