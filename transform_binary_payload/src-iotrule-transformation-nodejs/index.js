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

// Set default parametersv
var DECODER_PATH = "/opt/node/"
const DECODER_SUFFUX = ".js"

// Read command line parameters
var command_line_args = process.argv.slice(2);

// Allow to override decoder path to run local tests
if (command_line_args.length == 1 && command_line_args[0] == "local") {
    DECODER_PATH = "../src-payload-decoders/node/"
}


global.decoders = new Map()

var fs = require('fs');
var vm = require('vm');
var includeInThisContext = function (path) {
    var code = fs.readFileSync(path);
    vm.runInThisContext(code, path);
}.bind(this);

exports.handler = async function (event, context) {
    console.log('## EVENT: ' + JSON.stringify(event))

    // Read input parameters
    input_base64 = event.PayloadData
    payload_decoder_name = event.PayloadDecoderName
    device_id =
        fport = event.WirelessMetadata.LoRaWAN.FPort;

    // Logging
    console.log("Decoding payload " + input_base64 + " with fport " + fport + " using decoder " + payload_decoder_name)


    // Convert base64 payload into bytes
    let bytes = Uint8Array.from(Buffer.from(input_base64, 'base64'))


    try {

        // Cache the decoder function if not done yet
        if (!global.decoders.has(payload_decoder_name)) {
            includeInThisContext(DECODER_PATH + payload_decoder_name + DECODER_SUFFUX);
            global.decoders.set(payload_decoder_name, decodeUplink)
        }

        // Execute the decoder
        decoded = (global.decoders.get(payload_decoder_name))({
            "fPort": fport,
            "bytes": bytes
        })

        console.log("Decoded payload is " + JSON.stringify(decoded))

        // Check if decoder has returned any errors
        if (decoded.hasOwnProperty("errors")) {
            console.log("Error decoding :" + decoded.errors)
            throw ("Error decoding:" + decoded.errors)
        }

        result = decoded.data
        result.status = 200
        result.decoder_name = payload_decoder_name
        console.log("Returning result " + JSON.stringify(result))
        return result;
    } catch (e) {
        // Perform exception handling
        console.log(e)

        result = {
            "status": 500,
            "errorMessage": e,
            "decoder_name": payload_decoder_name
        }
        return result;


    }

}




