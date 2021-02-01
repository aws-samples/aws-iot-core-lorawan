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

# Allowed payload type values. This array will be used for validation of the "type" attribute for a
# handle of a Lambda function. For each value in the list below, you should import a module with the
# identical name.
#
# This module must implement "dict_from_payload(payload: str)" function which takes binary payload as
# an input and returns a dict with decoded attribute values.
#
# If you want to implement additional binary decoders:
# please add name of your binary decoder (e.g. "mylorawandevice") here (see "Step 4" above)
VALID_PAYLOAD_DECODER_NAMES = ["sample_device",
                               "dragino_lht65", "axioma_w1", "tabs_objectlocator",
                               "elsys"]

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
        WirelessDeviceId : str
            Device Id
        WirelessMetadata : json
            Metadata
        PayloadData : str
            Base64 encoded input payload
        PayloadDecoderName : string
            The value of this attribute defines the name of a Python module which will be used to perform binary decoding. If value of "type" is for example "sample_device", then this function will perform an invocation of "sample_device.dict_from_payload" function. For this approach to work, you  have to import the necessary modules, e.g. by performing a "import sample_device01" command in the beginning of this file.

        Returns
        -------
        This function returns a JSON object with the following keys:

        - status: 200 or 500
        - transformed_payload: result of calling "decode_{event.type}"      (only if status == 200)
        - error_type                                                        (only if status == 500)
        - error_message                                                     (only if status == 500)
        - stackTrace                                                        (only if status == 500)


    """
    logger.info("Received event: %s" % json.dumps(event))

    # Store event input and perform input validation
    input_base64 = event.get("PayloadData")
    payload_decoder_name = event.get("PayloadDecoderName")

    # Validate existence of payload type
    if (payload_decoder_name is None):
        raise InvalidInputException(
            "PayloadDecoderName is not specified")

    # Validate  if payload type is in the list of allowed values
    if (not payload_decoder_name in VALID_PAYLOAD_DECODER_NAMES):
        raise InvalidInputException(
            "PayloadDecoderName have one of the following values:"+(".".join(VALID_PAYLOAD_DECODER_NAMES)))

    logger.info(f"Base64 input={input_base64}, Type={payload_decoder_name}")

    # WirelessDeviceId and WirelessMetadata are not used in this example but included
    # for the case you will need it in your project

    # device_id = event.get("WirelessDeviceId")
    # metadata = event.get("WirelessMetadata")

    # Derive a name of a payload conversion function based on the value of 'type' attribute
    conversion_function_name = f"{payload_decoder_name}.dict_from_payload"
    logger.info(f"Function name={conversion_function_name}")

    # Invoke a payload conversion function and return a result
    try:
        result = eval(conversion_function_name)(input_base64)
        result["status"] = 200
        logger.info(result)
        return result

    except Exception as exp:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback)
        result = {
            "status": 500,
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "stackTrace": traceback_string
        }
        logger.error(result)
        return result
