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
import traceback
import logging
import sys
from time import time


import rfi_power_switch

# Setup  logging
logger = logging.getLogger("PayloadDecoder")
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """ Transforms a binary payload by invoking "decode_{event.type}" function
        Parameters
        ----------
        DeviceId : str
            Device Id
        ApplicationId : int
            LoRaWAN Application Id / Port number
        PayloadData : str
            Base64 encoded input payload


        Returns
        -------
        This function returns a JSON object with the following keys:

        - status: 200 or 500
        - transformed_payload: result of calling "{PayloadDecoderName}.dict_from_payload"      (only if status == 200)
        - lns_payload: a representation of payload as received from an LNS
        - error_type                                                        (only if status == 500)
        - error_message                                                     (only if status == 500)
        - stackTrace                                                        (only if status == 500)


    """

    logger.info("Received event: %s" % json.dumps(event))

    input_base64 = event.get("PayloadData")
    device_id = event.get("WirelessDeviceId")
    metadata = event.get("WirelessMetadata")["LoRaWAN"]

    try:

        # Invoke a payload conversion function
        decoded_payload = rfi_power_switch.dict_from_payload(
            event.get("PayloadData"))

        # Define the output of AWS Lambda function in case of successful decoding
        decoded_payload["status"] = 200

        result = decoded_payload
        
        logger.info(result)
        return result

    except Exception as exp:

        logger.error(f"Exception {exp} during binary decoding")

        raise exp
