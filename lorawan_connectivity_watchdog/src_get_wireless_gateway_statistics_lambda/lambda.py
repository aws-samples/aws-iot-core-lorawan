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
import time
import traceback
import dateutil.parser
import logging
import uuid
import os
import sys
import datetime

# Define parameters for check of input validity
OBLIGATORY_PARAMETERS = []

# Function name for logging
FUNCTION_NAME = "IngestWirelessGatewayStatisticsToIoTEvents"

# Setup logging
logger = logging.getLogger(FUNCTION_NAME)
logger.setLevel(logging.INFO)

# Create an instance of a low-level client representing AWS IoT Core for LoRaWAN
client_iotwireless = boto3.client("iotwireless")
client_iotevents = boto3.client("iotevents-data")

if "IOT_EVENTS_INPUT_NAME" in os.environ:
    IOT_EVENTS_INPUT_NAME = os.environ.get("IOT_EVENTS_INPUT_NAME")
else:
    raise Exception("IOT_EVENTS_INPUT_NAME is not defined")

if "TEST_MODE" in os.environ and os.environ.get("TEST_MODE") == 'true':
    TEST_MODE = True
else:
    TEST_MODE = False

logger.info(f"TEST_MODE is {TEST_MODE}")


class MissingParameterInEvent(Exception):
    """Raised when the parameter is missing"""
    pass


def put_events_message(gateway_id: str, last_uplink_received_timestamp_ms: int, connection_status: str) -> None:

    iot_events_input_payload = {
        "gatewayid": gateway_id,
        "last_connection_status": connection_status,
        "last_uplink_received_timestamp_ms": last_uplink_received_timestamp_ms,
        "timestamp_iso8601": datetime.datetime.now().isoformat()
    }

    logger.info(f"Calling IoT Events batch_put_message with payload {json.dumps(iot_events_input_payload)}")
    client_iotevents.batch_put_message(
        messages=[
            {
                'inputName': IOT_EVENTS_INPUT_NAME,
                'messageId': str(uuid.uuid4()),
                'payload': json.dumps(
                    iot_events_input_payload
                )
            },
        ]
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

    gateway_ids = []
    errors = []

    try:
        if ("GatewayId" in event):
            gateway_ids = [event["GatewayId"]]
        else:
            gateway_ids = map(lambda entry: entry["Id"], client_iotwireless.list_wireless_gateways()["WirelessGatewayList"])

        if TEST_MODE and ("test" in event):
            logger.info(f"Test event data {event.get('test')}")
            put_events_message(event.get("test").get("gatewayid"),
                               connection_status=event.get("test").get("connection_status"), last_uplink_received_timestamp_ms=int(event.get("test").get("last_uplink_received_timestamp_ms")))

        # Iterate over all wireless gateways
        for gateway_id in gateway_ids:
            logger.info(f"Processing gateway with id {gateway_id}")

            # Retrieve gateway statistics
            response = client_iotwireless.get_wireless_gateway_statistics(WirelessGatewayId=gateway_id)
            logger.info(f"Gateway statistics: {response}")

            if ("ConnectionStatus" in response):
                updated_connection_status = response.get("ConnectionStatus")
                updated_last_uplink_received_timestamp_ms = round(dateutil.parser.isoparse(response.get("LastUplinkReceivedAt")).timestamp() * 1000)
                logger.info(f"Gateway {gateway_id}, Last uplink ts={updated_last_uplink_received_timestamp_ms}, connection status={updated_connection_status}")

                put_events_message(gateway_id,
                                   connection_status=updated_connection_status, last_uplink_received_timestamp_ms=updated_last_uplink_received_timestamp_ms)
            else:
                logger.info(f"Gateway {gateway_id} is lacking 'ConnectionStastus', must has never yet connected. Ignoring it.")

        result = {
            "status": 200,
            "timestamp_ms": str(round(time.time())),
            "errors": errors
        }
        return result
    except Exception as e:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback)

        logger.error("Error: " + str(e))
        errors.append({
            "errormessage": str(e),
            "traceback": traceback_string
        })
        result = {
            "status": 500,
            "timestamp_ms": str(round(time.time())),
            "errors": errors
        }
        return result
