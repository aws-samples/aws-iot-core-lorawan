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

#
# If you want to implement additional binary decoders, please follow these steps:
# Step 1: Choose a name for a binary decoder, for example "mylorawandevice".
# Step 2: Implement binary decoder in a file "mylorawandevice.py". This file must contain "dict_from_payload(input:str)"
# function, which takes a binary payload as an input and returns a dict with the decoded results.
# Step 3: Add "import mylorawandevice.py" below
# Step 4: Add "mylorawandevice" as a value to VALID_PAYLOAD_DECODER_NAMES
#

import json
import traceback
import logging
import sys
import os
from time import time

import boto3


# Function name for logging
FUNCTION_NAME = "WriteToTimestream"

# Setup logging
logger = logging.getLogger(FUNCTION_NAME)
logger.setLevel(logging.INFO)

# Define exception to be raised if input is lacking or invalid


class InvalidInputException(Exception):
    pass


# Instantiate boot3 client for Timestream
timestream = boto3.client('timestream-write')

# Read and validate existence of environment variables
# Amazon Timestream database name
DB_NAME = os.environ.get('DB_NAME')
# Amazon Timestream table names
TABLE_NAME_TELEMETRY = os.environ.get('TABLE_NAME_TELEMETRY')
TABLE_NAME_METADATA = os.environ.get('TABLE_NAME_METADATA')


def dict_to_records(data):
    records = []
    for k, v in data.items():
        records.append({
            'MeasureName': k,
            'MeasureValue': str(v)
        })
    return records


def lambda_handler(event, context):
    """ Writes the output of 'TransformLoRaWANBinaryPayloadForTimestreamFunction' into Amazon Timestream 
        Parameters
        ----------
        transformed message : JSON, e.g.

         {
            "transformed_payload": {
                "temperature": 22.6,
                "humidity": 41,
                "light": 39,
                "motion": 6,
                "co2": 776,
                "vdd": 3426,
                "status": 200,
                "decoder_name": "elsys",
                "WirelessDeviceId": "57728ff8-5d1d-4130-9de2-f004d8722bc2",
                "DevEui": "a84041d55182720b"
            },
            "lns_payload": {
                "WirelessDeviceId": "57728ff8-5d1d-4130-9de2-f004d8722bc2",
                "WirelessMetadata": {
                "LoRaWAN": {
                    "DataRate": 0,
                    "DevEui": "a84041d55182720b",
                    "FPort": 2,
                    "Frequency": 867900000,
                    "Gateways": [
                    {
                        "GatewayEui": "dca632fffe45b3c0",
                        "Rssi": -76,
                        "Snr": 9.75
                    }
                    ],
                    "Timestamp": "2020-12-07T14:41:48Z"
                }
                },
                "PayloadData": "AQDiAikEACcFBgYDCAcNYg=="
            },
            "timestamp": 1639411314702
            }
        Please note that for each of key/value pair inside "payload" attribute a new  measurement with type 
        measure_value::double will be written in a "lorawan2timestreamLoRaWANTelemetryTable" table

        Please note that for each entry in "LoRaWAN.Gateways"  measurements will be written lorawan2timestreamLoRaWANMetadataTable" table:
        - Rssi
        - Snr

        Returns
        -------
        This function returns a JSON object with the following keys:

        - status: 200 on successful

        Exception is raised by this function in case of an error.


    """

    try:
        logger.info("Received event: %s" % json.dumps(event))

        # Store event input
        input_transformed = event.get("transformed_payload")
        device_id = event.get("lns_payload").get("WirelessDeviceId")
        metadata = event.get("lns_payload").get("WirelessMetadata")["LoRaWAN"]

        logger.info("Metadata: % s" % json.dumps(metadata))

        # Define Amazon Timestream dimensions
        dimensions = [
            {'Name': 'DeviceId', 'Value': str(device_id)},
            {'Name': 'DevEui', 'Value': str(metadata["DevEui"])},
            {'Name': 'FPort', 'Value': str(metadata["FPort"])},
        ]

        logger.info("Dimensions: %s" % json.dumps(dimensions))

        if "status" in input_transformed:
            del input_transformed["status"]
        if "decoder_name" in input_transformed:
            del input_transformed["decoder_name"]
        if "WirelessMetadata" in input_transformed:
            del input_transformed["WirelessDeviceId"]
        if "DevEui" in input_transformed:
            del input_transformed["DevEui"]
        

        # Convert decoded payload to Amazon Timestream records
        payload_records = dict_to_records(input_transformed)
        logger.info("Payload records: % s" %
                    json.dumps(payload_records))

        # Write records to Amazon Timestream table TABLE_NAME_TELEMETRY
        timestream.write_records(DatabaseName=DB_NAME,
                                 TableName=TABLE_NAME_TELEMETRY,
                                 CommonAttributes={
                                     'Dimensions': dimensions,
                                     'MeasureValueType': 'DOUBLE',
                                     'Time': str(int(time() * 1000)),
                                     'TimeUnit': 'MILLISECONDS'
                                 },
                                 Records=payload_records)

        # Iterate over each of gateways in LoRaWAN metadata
        for gateway_metadata in metadata["Gateways"]:
            dimensions_per_gateway = dimensions.copy()

            # Add GatewayEUI to dimensions
            dimensions_per_gateway.append(
                {'Name': "GatewayEui", 'Value': str(gateway_metadata["GatewayEui"])})
            logger.info("Dimensions for gateway: %s" %
                        json.dumps(dimensions_per_gateway))

            # Create Amazon Timestream records
            records_per_gateway = dict_to_records({
                "Rssi": gateway_metadata["Rssi"],
                "Snr": gateway_metadata["Snr"],
                "Frequency": metadata["Frequency"],
                "DataRate": metadata["DataRate"]

            })

            # Write records to Amazon Timestream table TABLE_NAME_METADATA
            timestream.write_records(DatabaseName=DB_NAME,
                                     TableName=TABLE_NAME_METADATA,
                                     CommonAttributes={
                                         'Dimensions': dimensions_per_gateway,
                                         'MeasureValueType': 'DOUBLE',
                                         'Time': str(int(time() * 1000)),
                                         'TimeUnit': 'MILLISECONDS'
                                     },
                                     Records=records_per_gateway)

        # Define the output of AWS Lambda function
        result = {
            "status": 200
        }
        logger.info(result)
        return result

    except Exception as exp:

        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback)

        # Define the error message

        result = {
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "stackTrace": traceback_string
        }
        logger.error("Exception during execution: %s" % json.dumps(result))

        # Finish AWS Lambda processing with an error
        raise exp
