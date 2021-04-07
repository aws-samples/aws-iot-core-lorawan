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


# Import binary decoders.
#
# If you want to implement additional binary decoders:
# Please add "import mylorawandevice" for your binary decoders here (see "Step 3" above)

import sample_device
import dragino_lht65
import axioma_w1
import tabs_objectlocator
import elsys
import globalsat_lt100
import dragino_lgt92
import dragino_lse01
import dragino_lbt1
import dragino_lds01
import nas_um3080
import adeunis_ftd2
import adeunis_dc_v2

# Allowed payload type values. This array will be used for validation of the "type" attribute for a
# handle of a Lambda function. For each value in the list below, you should import a module with the
# identical name.
#
# This module must implement "dict_from_payload(payload: str)" function which takes binary payload as
# an input and returns a dict with decoded attribute values.
#
# If you want to implement additional binary decoders:
# please add name of your binary decoder (e.g. "mylorawandevice") here (see "Step 4" above)
VALID_PAYLOAD_DECODER_NAMES = ["sample_device", "axioma_w1", "tabs_objectlocator",
                               "dragino_lht65", "dragino_lgt92", "dragino_lse01", "dragino_lbt1", "dragino_lds01",
                               "elsys", "globalsat_lt100", "nas_um3080", "adeunis_ftd2", "adeunis_dc_v2"]

# Function name for logging
FUNCTION_NAME = "ConvertBinaryPayload"

# Setup logging
logger = logging.getLogger(FUNCTION_NAME)
logger.setLevel(logging.INFO)

# Define exception to be raised if input is lacking or invalid


class InvalidInputException(Exception):
    pass


def lambda_handler(event, context):
    """ Transforms a binary payload by invoking "decode_{event.type}" function
        Parameters 
        ----------
        PayloadData : str (obligatory parameter)
            Base64 encoded input payload

        PayloadDecoderName : string (obligatory parameter)
            The value of this attribute defines the name of a Python module which will be used to perform binary decoding. If value of "type" is for example "sample_device", then this function will perform an invocation of "sample_device.dict_from_payload" function. For this approach to work, you  have to import the necessary modules, e.g. by performing a "import sample_device01" command in the beginning of this file.

        WirelessDeviceId : str (optional parameter)
            Wireless Device Id

        WirelessMetadata : json (obligatory parameter)
            This parameter contains Metadata of transmission according to the example below.
            Obligatory element is: LoRaWAN.FPort
            All other elements are optional and ignored in the current implementation.

            Sample input:
            {
            "LoRaWAN": {
                "DataRate": 0,
                "DevEui": "a84041d55182720b",
                "FPort": 21,
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

        Returns
        -------
        This function returns a JSON object with the following keys:

        - status: 200 or 500
        - transformed_payload: output of function "decode_{event.type}"     (only if status == 200)
        - error_type                                                        (only if status == 500)
        - error_message                                                     (only if status == 500)
        - stackTrace                                                        (only if status == 500)


    """
    logger.info("Received event: %s" % json.dumps(event))

    # Store event input and perform input validation
    input_base64 = event.get("PayloadData")
    payload_decoder_name = event.get("PayloadDecoderName")

    # Validate existence of payload type
    if payload_decoder_name is None:
        raise InvalidInputException(
            "PayloadDecoderName is not specified")

    # Validate  if payload type is in the list of allowed values
    if payload_decoder_name not in VALID_PAYLOAD_DECODER_NAMES:
        raise InvalidInputException(
            "PayloadDecoderName have one of the following values:"+(".".join(VALID_PAYLOAD_DECODER_NAMES)))

    logger.info(f"Base64 input={input_base64}, Type={payload_decoder_name}")

    # Retrieve FPort from the metadata. In case FPort or surrounding attributes is missing,
    # the function will intentionally not fail but proceed with fPort == None.
    # The binary decoder function is expected to handle fPort == None.
    fPort = None
    if "WirelessMetadata" in event:
        if "LoRaWAN" in event.get("WirelessMetadata"):
            if "FPort" in event.get("WirelessMetadata").get("LoRaWAN"):
                fPort = event.get("WirelessMetadata").get(
                    "LoRaWAN").get("FPort")
            else:
                logger.warn(
                    "Attribute 'WirelessMetadata.LoRaWAN' is missing. Will proceed with fPort == None.")
        else:
            logger.warn(
                "Attribute 'WirelessMetadata.LoRaWAN' is missing. Will proceed with fPort == None.")
    else:
        logger.warn(
            "Attribute 'WirelessMetadata' is missing. Will proceed with fPort == None.")

    # Derive a name of a payload conversion function based on the value of 'type' attribute
    conversion_function_name = f"{payload_decoder_name}.dict_from_payload"
    logger.info(f"Function name={conversion_function_name}")

    # Invoke a payload conversion function and return a result
    try:
        result = eval(conversion_function_name)(input_base64, fPort)
        result["status"] = 200
        result["decoder_name"] = payload_decoder_name
        logger.info(result)
        return result

    except Exception as exp:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback)
        result = {
            "status": 500,
            "decoder_name": payload_decoder_name,
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "stackTrace": traceback_string
        }
        logger.error(result)
        return result
