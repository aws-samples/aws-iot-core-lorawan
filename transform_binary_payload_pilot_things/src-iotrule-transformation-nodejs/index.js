// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

// Permission is hereby granted, free of charge, to any person obtaining a copy of this
// software and associated documentation files (the "Software"), to deal in the Software
// without restriction, including without limitation the rights to use, copy, modify,
// merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
// permit persons to whom the Software is furnished to do so.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
// INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
// PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
// HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
// OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
// SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

const fetch = require("node-fetch")
const VALID_PRODUCT_ID_REGEX = /^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$/;

exports.handler = async function (event, context) {
    /* Transforms a binary payload by the Pilot Things decoding service.
            Parameters 
            ----------
            event.PayloadData : str (obligatory parameter)
                Base64 encoded input payload
    
            event.PayloadDecoderProductId : string (obligatory parameter)
                The value of this attribute defines the GUID of the decoder which will be used by the Pilot Things decoding service.
    
    
            Returns
            -------
            This function returns a JSON object with the following keys:
    
            - status: 200 or 500
            - product_id: value of input parameter event.PayloadDecoderProductId
            - transformed_payload: output of Pilot Things decoding service      (only if status == 200)
            - error_message                                                     (only if status == 500)
    
    */


    console.log('## EVENT: ' + JSON.stringify(event))

    // Read input parameters
    const input_base64 = event.PayloadData
    const product_id = event.PayloadDecoderProductId
    const api_key = process.env.PILOT_THINGS_SERVICE_API_KEY

    // Check if product ID mathes the regex
    if (!product_id.match(VALID_PRODUCT_ID_REGEX)) {
        return {
            "status": 500,
            "errorMessage": "PayloadDecoderProductId must be a GUID",
            "product_id": product_id
        }
    }

    // Logging
    console.log("Decoding payload " + input_base64 + " using product " + product_id)


    // Convert base64 payload into hex string
    const input_hex = Buffer.from(input_base64, 'base64').toString("hex")
    const fetchResult = await fetch("https://sensor-library.pilot-things.net/decode", {
        method: "POST",
        headers: {
            "x-api-key": api_key
        },
        body: JSON.stringify({
            productId: product_id,
            payload: input_hex
        })
    })

    if (fetchResult.ok) {
        const result = {
            ...await fetchResult.json(),
            status: 200,
            product_id: product_id
        };

        console.log("Returning result " + JSON.stringify(result))
        return result;
    } else {
        const error = "Decoding service failed with error code " + fetchResult.status + " and body " + await fetchResult.json();
        console.log(error);

        return {
            "status": 500,
            "errorMessage": error,
            "product_id": product_id
        }
    }
}




