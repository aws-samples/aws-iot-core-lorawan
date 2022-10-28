# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import boto3
import traceback
import logging
import os
import sys

# Define parameters for check of input validity
OBLIGATORY_PARAMETERS = ["GatewayId", "MetricName", "MetricValueNumeric"]

# Function name for logging
FUNCTION_NAME = "PutCloudwatchMetrics"

# Setup logging
logger = logging.getLogger(FUNCTION_NAME)
logger.setLevel(logging.INFO)

# Create an instance of a low-level client representing AWS IoT Core for LoRaWAN
client_iotwireless = boto3.client("iotwireless")
client_cloudwatch = boto3.client("cloudwatch")
client_iotevents = boto3.client("iotevents-data")


if "TEST_MODE" in os.environ and os.environ.get("TEST_MODE") == 'true':
    TEST_MODE = True
else:
    TEST_MODE = False

logger.info(f"TEST_MODE is {TEST_MODE}")


class MissingParameterInEvent(Exception):
    """Raised when the parameter is missing"""
    pass


def put_cloudwatch_metric_number(metric_name: str, metric_value: int, gatewayid: str) -> None:
    response = client_cloudwatch.put_metric_data(
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name': 'GATEWAYID',
                        'Value': gatewayid
                    }
                ],
                'Unit': 'None',
                'Value': metric_value
            },
        ],
        Namespace='LoRaWAN'
    )


def handler(event, context):
    logger.info("Received event: %s" % json.dumps(event))

    # Check if all the necessary params are included and return an error ststus otherwise
    for i in OBLIGATORY_PARAMETERS:
        if i not in event:
            logger.error(f"Parameter {i} missing ")
            return {
                "status": 500,
                "errormessage": f"Parameter {i} missing"
            }

    try:

        response = put_cloudwatch_metric_number(metric_name=event.get("MetricName"),
                                                metric_value=event.get("MetricValueNumeric"),
                                                gatewayid=event.get("GatewayId")
                                                )
        result = {
            "status": 200,
            "trace": response
        }
        return result
    except Exception as e:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback)

        logger.error("Error: " + str(e))
        result = {
            "status": 500,
            "errors": {
                "errormessage": str(e),
                "traceback": traceback_string
            }
        }
        return result
