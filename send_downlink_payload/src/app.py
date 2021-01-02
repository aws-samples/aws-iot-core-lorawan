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
#
# You can use a following test event in AWS Lambda console (after adjusting a DeviceId).
# Note that PayloadData is base64-encoded twice to simulate behaviour of the AWS IoT Rule
#  {
#   "WirelessDeviceId": "77e8cf02-35c4-4d38-a264-ba9ee5947fb4",
#   "FPort": 2,
#   "PayloadData": "RFBBQUFBUzNDSVFOU0FBPQ==",
#   "TransmitMode": 1
# }

import json
import boto3
import base64
import traceback
import logging
import sys


# Define parameters for check of input validity
OBLIGATORY_PARAMETERS = ["WirelessDeviceId",
                         "PayloadData", "TransmitMode", "FPort"]

# Function name for logging
FUNCTION_NAME = "SendDownlinkPayload"

# Setup logging
logger = logging.getLogger(FUNCTION_NAME)
logger.setLevel(logging.INFO)

# Create an instance of a low-level client representing AWS IoT Core for LoRaWAN
client = boto3.client("iotwireless")


class MissingParameterInEvent(Exception):
    """Raised when the parameter is missing"""
    pass


def lambda_handler(event, context):
    """ Invokes a AWS IoT Core for LoRaWAN send_data_to_device API based on parameters provided in Event
        Parameters
        ----------
        "WirelessDeviceId", "FPort", "PayloadData","TransmitMode"
        DeviceId : str
            AWS IoT Core for LoRaWAN Device Id
        FPort : int
            Port number
        PayloadData : str,  Base64 encoded twice
            Please note this this function expects that a binary payload is encoded twice using Base64.

            To understand the reason for double encoding, let's consider how a binary payload 
            (e.g. 0x414243) is processed in this sample:

            1. You initiate sending of data to a LoRaWAN devices by invocation of the AWS IoT Rule
               SendDataToWirelessDeviceRule. The rule can be invoked either by due to subscription
               as define in WHERE clause (https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-from.html) or via Basic Ingest (https://docs.aws.amazon.com/iot/latest/developerguide/iot-basic-ingest.html).

               For example you can invoke SendDataToWirelessDeviceRule by publishing to the MQTT broker topic `cmd/downlink/c7867453-5404-4680-a081-0fda2902110a`. You could also perform Basic Ingest by publishing to $aws/rules/SendDataToWirelessDeviceRule/cmd/downlink/c7867453-5404-4680-a081-0fda2902110a .

            2. The AWS IoT Rule SendDataToWirelessDeviceRule expects Base64-encoded payload as an input.

            3. Before AWS IoT Rule SendDataToWirelessDeviceRule can pass a payload to this AWS Lambda function, the payload have to be Base64-encoded once again. Please consult 
            https://docs.aws.amazon.com/iot/latest/developerguide/binary-payloads.html for details.

        TransmitMode : int
            Please consult AWS IoT Core for LoRaWAN documentation for details.

        """
    logger.info("Received event: %s" % json.dumps(event))

    # Check if all the necessary params are included and return an error ststus otherwise
    for i in OBLIGATORY_PARAMETERS:
        if not i in event:
            logger.error(f"Parameter {i} missing ")
            return {
                "status": 500,
                "errormessage": f"Parameter {i} missing"
            }

    (device_id, fport, transmit_mode, payload_data) = (
        event["WirelessDeviceId"], event["FPort"], event["TransmitMode"], event["PayloadData"])

    # Decode base64 payload. Please note that decoded payload will still have Base64
    # format. Please review the documentation of this function for details.
    print(f"Payload to decode : {payload_data}")
    payload_data_decoded = base64.b64decode(payload_data).decode("utf-8")

    print(f"Decoded data : {payload_data_decoded}")

    try:
        response = client.send_data_to_wireless_device(TransmitMode=transmit_mode,
                                                       Id=device_id,
                                                       WirelessMetadata={"LoRaWAN": {"FPort": fport}}, PayloadData=payload_data_decoded)
    except client.exceptions.ResourceNotFoundException as e:
        logger.error("Error calling LoRaWAN for AWS IoT Core API : " + str(e))
        return {
            "status": 500,
            "errormessage": f"Device with WirelessDeviceId {device_id} not found"
        }
    except Exception as e:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback)

        logger.error("Error calling LoRaWAN for AWS IoT Core API : " + str(e))
        return {
            "status": 500,
            "errormessage": str(e),
            "traceback": traceback_string
        }

    result = {
        "status": 200,
        "RequestId": response["ResponseMetadata"]["RequestId"],
        "MessageId": response["MessageId"],
        # Parameter trace below is for debugging and prototyping purposes and should
        # be removed in a production deployment unless needed
        "ParameterTrace": {
            "PayloadData": payload_data_decoded,
            "WirelessDeviceId": device_id,
            "Fport": fport,
            "TransmitMode": transmit_mode
        }
    }

    print(f"Successfull API call result {json.dumps(result)}")

    return result
