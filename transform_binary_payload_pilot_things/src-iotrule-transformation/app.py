# Copyright Pilot Things. All Rights Reserved.
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
import logging
import re
import requests
import base64
import os

# Function name for logging
FUNCTION_NAME = "ConvertBinaryPayload"

# Setup logging
logger = logging.getLogger(FUNCTION_NAME)
logger.setLevel(logging.INFO)

# Define exception to be raised if input is lacking or invalid
class InvalidInputException(Exception):
    pass

# Define regex used to pre-validate product ID
VALID_PRODUCT_ID_REGEX = re.compile("^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$")

def lambda_handler(event, context):
    """ Transforms a binary payload by the Pilot Things decoding service.
        Parameters 
        ----------
        PayloadData : str (obligatory parameter)
            Base64 encoded input payload

        PayloadDecoderProductId : str (obligatory parameter)
            The value of this attribute defines the GUID of the decoder which will be used by the Pilot Things decoding service.

        Returns
        -------
        This function returns a JSON object with the following keys:

        - status: 200 or 500
        - transformed_payload: output of Pilot Things decoding service      (only if status == 200)
        - error_type                                                        (only if status == 500)
        - error_message                                                     (only if status == 500)
        - stackTrace                                                        (only if status == 500)


    """
    logger.info("Received event: %s" % json.dumps(event))

    # Store event input and perform input validation
    input_base64 = event.get("PayloadData")
    product_id = event.get("PayloadDecoderProductId")
    api_key = os.environ["PILOT_THINGS_SERVICE_API_KEY"]

    # Validate existence of payload type
    if product_id is None:
        raise InvalidInputException("PayloadDecoderProductId is not specified")

    # Validate  if payload type is in the list of allowed values
    if not VALID_PRODUCT_ID_REGEX.match(product_id):
        raise InvalidInputException("PayloadDecoderProductId must be a GUID")

    logger.info(f"Base64 input={input_base64}, Product ID={product_id}")

    # Convert Base64 to a hexadecimal string
    input_hex = base64.b64decode(input_base64).hex()

    # Invoke the decoding service and return a result
    r = requests.post("https://sensor-library.pilot-things.net/decode", headers={'x-api-key': api_key}, json={
        'productId': product_id,
        'payload': input_hex
    })
    # Check for errors
    r.raise_for_status()

    result = r.json()
    result["status"] = 200
    result["product_id"] = product_id
    logger.info(result)
    return result
